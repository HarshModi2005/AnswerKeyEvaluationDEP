"""
Google Sheets Service
=====================
Reads student lists from Google Sheets and writes marks back.
Entry numbers are matched using the pattern yyyyBBBnnnn (e.g. 2023CSB1122).
Names are cross-verified — mismatches are flagged but marks are still written.
Supports writing 'comments' if a column is present.
Supports writing per-question marks if columns like '1', 'Q1', '2', 'Q2' are present.
"""

import os
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build
from typing import List, Dict, Optional, Tuple, Any


class SheetsService:
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',  # Read + Write
    ]

    # Aliases for auto-detecting column headers
    ENTRY_NUMBER_ALIASES = {
        'entry number', 'entry_number', 'entry no', 'entry no.',
        'roll number', 'roll_number', 'roll no', 'roll no.',
        'enrollment', 'enrollment number', 'enrollment no',
        'id', 'student id', 'student_id', 'reg number',
        'registration number', 'reg no', 'reg no.',
    }

    NAME_ALIASES = {
        'name', 'student name', 'student_name', 'full name',
        'full_name', 'candidate name',
    }

    MARKS_ALIASES = {
        'marks', 'mark', 'score', 'total', 'grade', 'result',
        'total marks', 'total_marks', 'total score', 'total_score',
        'obtained marks', 'obtained_marks', 'marks obtained',
    }
    
    COMMENTS_ALIASES = {
        'comments', 'comment', 'remarks', 'remark', 'feedback', 'notes',
        'observation', 'observations', 'issues', 'issue'
    }

    # Regex for entry number format: yyyyBBBnnnn (e.g. 2023CSB1122)
    ENTRY_NUMBER_PATTERN = re.compile(
        r'(\d{4})\s*([A-Za-z]{2,4})\s*(\d{2,5})',
    )
    
    # Regex for question columns: "1", "Q1", "Q 1", "Question 1", "1a" (if simple digit)
    # We will support simple integers for now as per current pipeline.
    # Regex for question columns: 1, Q1, Q.1, Q-1, Question 1
    QUESTION_COLUMN_PATTERN = re.compile(
        r'^(?:q|ques|question)?[\s\.\-\_]*(\d+)$', 
        re.IGNORECASE
    )

    def __init__(self, credentials_path: str = "credentials.json"):
        self.creds = None
        self.service = None

        # Try to load credentials
        if not os.path.exists(credentials_path):
            env_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if env_path and os.path.exists(env_path):
                credentials_path = env_path

        if os.path.exists(credentials_path):
            try:
                self.creds = service_account.Credentials.from_service_account_file(
                    credentials_path, scopes=self.SCOPES
                )
                self.service = build('sheets', 'v4', credentials=self.creds)
                print("Sheets Service: Initialized with Service Account")
            except Exception as e:
                print(f"Sheets Service: Error loading credentials: {e}")
        else:
            print(f"Sheets Service: No credentials found at {credentials_path}")

    # ──────────────────────────────────────
    #  URL Parsing
    # ──────────────────────────────────────

    @staticmethod
    def parse_sheet_url(url: str) -> Tuple[str, Optional[str]]:
        """
        Extract spreadsheet ID and optional sheet name/GID from URL.
        """
        spreadsheet_id = url
        sheet_name = None

        match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
        if match:
            spreadsheet_id = match.group(1)

        return spreadsheet_id, sheet_name

    # ──────────────────────────────────────
    #  Entry Number Normalization
    # ──────────────────────────────────────

    @classmethod
    def _normalize_entry_number(cls, raw: str) -> Optional[str]:
        """Normalize to YYYYBBBNNNN."""
        if not raw or raw.lower() in ('unknown', 'none', 'n/a', ''):
            return None

        clean = raw.strip()
        m = cls.ENTRY_NUMBER_PATTERN.search(clean)
        if m:
            year = m.group(1)
            branch = m.group(2).upper()
            number = m.group(3)
            return f"{year}{branch}{number}"

        fallback = re.sub(r'[\s\-_./]', '', clean).upper()
        if len(fallback) >= 6:
            return fallback
        return None

    # ──────────────────────────────────────
    #  Name Cross-Verification
    # ──────────────────────────────────────

    @staticmethod
    def _check_name_mismatch(sheet_name: str, ocr_name: str, entry_number: str, row: int) -> Optional[str]:
        """Returns mismatch message string if names don't match."""
        if not sheet_name or not ocr_name:
            return None

        s = sheet_name.strip().lower()
        o = ocr_name.strip().lower()

        if not s or not o or s == 'unknown' or o == 'unknown':
            return None

        if s == o: return None
        
        s_parts = set(s.split())
        o_parts = set(o.split())
        if s_parts.intersection(o_parts): return None

        if s in o or o in s: return None

        for word in s_parts:
            if len(word) >= 3 and word in o: return None
        for word in o_parts:
            if len(word) >= 3 and word in s: return None

        return f"Name mismatch: Sheet='{sheet_name}' vs OCR='{ocr_name}'"

    # ──────────────────────────────────────
    #  Reading Student List
    # ──────────────────────────────────────

    def read_student_list(self, sheet_url: str) -> Dict:
        """Read the student list and detect columns."""
        if not self.service:
            raise RuntimeError("Sheets service not initialized. Check credentials.")

        spreadsheet_id, sheet_name = self.parse_sheet_url(sheet_url)

        spreadsheet = self.service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()

        sheets = spreadsheet.get('sheets', [])
        if not sheets:
            raise ValueError("Spreadsheet has no sheets")

        if not sheet_name:
            sheet_name = sheets[0]['properties']['title']

        range_name = f"'{sheet_name}'"
        result = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()

        values = result.get('values', [])
        if not values or len(values) < 2:
            raise ValueError("Sheet is empty or has no data rows")

        headers = values[0]
        columns = self._detect_columns(headers)

        if not columns.get('entry_number'):
            raise ValueError(
                f"Could not detect entry number column. Headers: {headers}. "
                f"Expected one of: {self.ENTRY_NUMBER_ALIASES}"
            )

        students = []
        entry_col = columns['entry_number']['index']
        name_col = columns.get('name', {}).get('index')
        comments_col = columns.get('comments', {}).get('index')

        for row_idx, row in enumerate(values[1:], start=2):
            entry_number = self._safe_get(row, entry_col, '').strip()
            if not entry_number:
                continue

            name = self._safe_get(row, name_col, '').strip() if name_col is not None else ''
            existing_comment = self._safe_get(row, comments_col, '') if comments_col is not None else ''

            students.append({
                "row": row_idx,
                "entry_number": entry_number,
                "name": name,
                "existing_comment": existing_comment
            })

        return {
            "spreadsheet_id": spreadsheet_id,
            "sheet_name": sheet_name,
            "columns": columns,
            "students": students,
        }

    # ──────────────────────────────────────
    #  Writing Marks
    # ──────────────────────────────────────

    def update_marks(self, sheet_url: str, results: List[Dict]) -> Dict:
        """
        Write marks, comments, AND per-question scores.
        """
        if not self.service:
            raise RuntimeError("Sheets service not initialized. Check credentials.")

        # Read current state
        sheet_data = self.read_student_list(sheet_url)
        spreadsheet_id = sheet_data['spreadsheet_id']
        sheet_name = sheet_data['sheet_name']
        columns = sheet_data['columns']
        students = sheet_data['students']

        # Check required columns
        if not columns.get('marks'):
            raise ValueError("No 'marks' column detected.")

        marks_col_letter = columns['marks']['letter']
        comments_col_letter = columns.get('comments', {}).get('letter')
        question_cols = columns.get('questions', {}) # Dict[int, Dict] {1: {index, letter}, ...}

        # Build lookup
        results_map = {}
        for r in results:
            raw = str(r.get('entry_number', '')).strip()
            normalized = self._normalize_entry_number(raw)
            if normalized:
                results_map[normalized] = r

        summary = {
            "updated": 0,
            "not_found_in_sheet": [],
            "not_found_in_results": [],
            "name_mismatches": [],
            "errors": [],
        }

        batch_data = []
        matched_normalized = set()

        # DEBUG
        print(f"DEBUG: Results Map Keys: {list(results_map.keys())}")

        for student in students:
            raw_entry = student['entry_number']
            normalized = self._normalize_entry_number(raw_entry)
            
            # DEBUG
            # print(f"DEBUG: Sheet Row {student['row']}: '{raw_entry}' -> Normalized: '{normalized}'")

            if not normalized:
                continue

            # 1. Try Entry Number Match
            if normalized in results_map:
                matched_normalized.add(normalized)
                result = results_map[normalized]
            else:
                # 2. Fallback: Try Name Match
                # Iterate through all results to find a name match
                found_by_name = None
                sheet_name_cleaned = student.get('name', '').strip().lower()
                
                if sheet_name_cleaned:
                    for r in results:
                        ocr_name_cleaned = r.get('name', '').strip().lower()
                        # Simple inclusion check or intersection
                        if not ocr_name_cleaned: continue
                        
                        # Use existing name check logic? Or simplified?
                        # If exact match or significant overlap
                        if sheet_name_cleaned == ocr_name_cleaned:
                            found_by_name = r
                            break
                        
                        # Split parts
                        s_parts = set(sheet_name_cleaned.split())
                        o_parts = set(ocr_name_cleaned.split())
                        intersection = s_parts.intersection(o_parts)
                        
                        # If at least 2 significant words match (e.g. "Harsh Modi")
                        if len(intersection) >= 2:
                            found_by_name = r
                            break
                        # Or if 1 word matches and total words is small, but be careful of "Kumar"
                        if len(intersection) >= 1 and len(s_parts) == 1 and len(o_parts) == 1:
                             found_by_name = r
                             break

                if found_by_name:
                    result = found_by_name
                    # mismatch_msg = f"Matched by Name ('{student['name']}') instead of ID ('{raw_entry}' vs OCR '{result.get('entry_number')}')"
                    # final_comments.append(mismatch_msg)
                else:
                    summary['not_found_in_results'].append(raw_entry)
                    continue

            # Check duplication (if multiple students map to same result? Not detecting here)
            
            score = result.get('total_score', 0)
            details = result.get('details', []) # List of dicts/objects
            
            # Compose comment
            final_comments = []
            ocr_comment = result.get('comments', '')
            if ocr_comment:
                final_comments.append(ocr_comment)

            mismatch_msg = self._check_name_mismatch(
                student.get('name', ''),
                result.get('name', ''),
                raw_entry,
                student['row']
            )
            if mismatch_msg:
                summary['name_mismatches'].append({
                    "entry_number": raw_entry,
                    "sheet_name": student['name'],
                    "ocr_name": result.get('name'),
                    "row": student['row']
                })
                final_comments.append(mismatch_msg)
            
            comment_str = "; ".join(final_comments)

            # 1. Update Total Score
            batch_data.append({
                "range": f"'{sheet_name}'!{marks_col_letter}{student['row']}",
                "values": [[score]]
            })
            
            # 2. Update Comment
            if comments_col_letter and comment_str:
                batch_data.append({
                    "range": f"'{sheet_name}'!{comments_col_letter}{student['row']}",
                    "values": [[comment_str]]
                })

            # 3. Update Per-Question Scores
            q_map = {}
            if isinstance(details, list):
                for d in details:
                    try:
                        if isinstance(d, dict):
                            qn = int(d.get('question_number', -1))
                            q_map[qn] = d
                        else:
                            qn = int(d.question_number)
                            q_map[qn] = d
                    except (ValueError, TypeError, AttributeError):
                        continue
            
            # DEBUG: Print details for the first matched student
            if len(matched_normalized) == 1:
                print(f"🔍 DEBUG: Inspecting first student {raw_entry}")
                print(f"   Details count: {len(details)}")
                print(f"   Q_MAP keys (int): {list(q_map.keys())}")
                print(f"   Question Cols keys (int): {list(question_cols.keys())}")
                
            for q_num, col_info in question_cols.items():
                col_letter = col_info['letter']
                
                if q_num in q_map:
                    q_data = q_map[q_num]
                    val_to_write = 0
                    
                    if isinstance(q_data, dict):
                        status = q_data.get('result', '')
                        val = q_data.get('score', 0)
                    else:
                        status = getattr(q_data, 'result', '')
                        val = getattr(q_data, 'score', 0)
                    
                    if status in ['multiple', 'unattempted', 'incorrect']:
                        val_to_write = 0
                    elif status == 'correct':
                        val_to_write = val # Should be full marks
                    else:
                         # Default fallback
                        val_to_write = val
                    
                    # Add to batch
                    batch_data.append({
                        "range": f"'{sheet_name}'!{col_letter}{student['row']}",
                        "values": [[val_to_write]]
                    })
                else:
                    # If the student didn't have data for this question (e.g. absent/error or not in answer key?)
                    # We can choose to write 0 or leave blank.
                    pass

        # Execute batch update
        if batch_data:
            try:
                # Split huge batches if necessary (Google limit is around 50k calls?? No, payload size)
                # Chunking 1000 updates at a time is safer
                chunk_size = 500
                for i in range(0, len(batch_data), chunk_size):
                    chunk = batch_data[i:i + chunk_size]
                    body = {
                        "valueInputOption": "RAW",
                        "data": chunk,
                    }
                    self.service.spreadsheets().values().batchUpdate(
                        spreadsheetId=spreadsheet_id,
                        body=body
                    ).execute()
                
                summary['updated'] = len(matched_normalized)
                print(f"✅ Updated {len(batch_data)} cells for {len(matched_normalized)} students.")
            except Exception as e:
                summary['errors'].append(f"Batch update failed: {str(e)}")
                print(f"❌ Batch update failed: {e}")

        return summary

    # ──────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────

    QUESTION_COLUMN_PATTERN = re.compile(
        r'^(?:q|ques|question)?[\s\.\-\_]*(\d+)$', 
        re.IGNORECASE
    )

    def _detect_columns(self, headers: List[str]) -> Dict:
        """
        Auto-detect columns including Question columns (1, Q1, etc.)
        """
        columns = {'questions': {}}
        
        # Helper to normalize
        def norm(h): return h.strip().lower()

        for idx, header_raw in enumerate(headers):
            h = norm(header_raw)
            col_letter = self._index_to_letter(idx)
            
            # 1. Entry Number (High Priority)
            if not columns.get('entry_number'):
                if h in self.ENTRY_NUMBER_ALIASES:
                    columns['entry_number'] = {"index": idx, "letter": col_letter, "header": header_raw}
                    continue

            # 2. Student Name
            if not columns.get('name'):
                 if h in self.NAME_ALIASES:
                    columns['name'] = {"index": idx, "letter": col_letter, "header": header_raw}
                    continue

            # 3. Marks / Total Score
            if not columns.get('marks'):
                 if h in self.MARKS_ALIASES:
                    columns['marks'] = {"index": idx, "letter": col_letter, "header": header_raw}
                    continue
            
            # 4. Comments
            if not columns.get('comments'):
                 if h in self.COMMENTS_ALIASES:
                    columns['comments'] = {"index": idx, "letter": col_letter, "header": header_raw}
                    continue

            # 5. Question Columns (Check regex)
            # Try matching "Q1", "Question 1", "1", etc.
            m = self.QUESTION_COLUMN_PATTERN.match(h)
            if m:
                try:
                    q_num = int(m.group(1))
                    # Prevent "1" from being confused if we want constraints, but usually Qs are 1..N
                    columns['questions'][q_num] = {"index": idx, "letter": col_letter, "header": header_raw}
                    continue
                except ValueError:
                    pass
            
            # 6. Fallback: If header is just an integer, treat as question
            if header_raw.strip().isdigit():
                 q_num = int(header_raw.strip())
                 if q_num not in columns['questions']:
                     columns['questions'][q_num] = {"index": idx, "letter": col_letter, "header": header_raw}

        if columns.get('questions'):
            print(f"📊 Detected {len(columns['questions'])} question columns: {sorted(list(columns['questions'].keys()))}")
        
        return columns

    @staticmethod
    def _index_to_letter(index: int) -> str:
        result = ""
        while True:
            result = chr(65 + (index % 26)) + result
            index = index // 26 - 1
            if index < 0:
                break
        return result

    @staticmethod
    def _safe_get(lst: list, idx: Optional[int], default=None):
        if idx is None or idx >= len(lst):
            return default
        return lst[idx]
