"""
Google Sheets Service
=====================
Reads student lists from Google Sheets and writes marks back.
Entry numbers are matched using the pattern yyyyBBBnnnn (e.g. 2023CSB1122).
Names are cross-verified — mismatches are flagged but marks are still written.
"""

import os
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build
from typing import List, Dict, Optional, Tuple


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

    # Regex for entry number format: yyyyBBBnnnn (e.g. 2023CSB1122)
    ENTRY_NUMBER_PATTERN = re.compile(
        r'(\d{4})\s*([A-Za-z]{2,4})\s*(\d{2,5})',
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
        
        Handles:
        - https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
        - https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit#gid=0
        - https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit?usp=sharing
        
        Returns:
            (spreadsheet_id, sheet_name_or_none)
        """
        spreadsheet_id = url
        sheet_name = None

        # Extract spreadsheet ID from URL
        match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
        if match:
            spreadsheet_id = match.group(1)

        # Try to extract gid for specific sheet
        gid_match = re.search(r'[#&?]gid=(\d+)', url)
        if gid_match:
            # We'll resolve gid to sheet name later if needed
            pass

        return spreadsheet_id, sheet_name

    # ──────────────────────────────────────
    #  Entry Number Normalization
    # ──────────────────────────────────────

    @classmethod
    def _normalize_entry_number(cls, raw: str) -> Optional[str]:
        """
        Normalize an entry number to the canonical format: YYYYBBBNNNN (uppercase).
        
        E.g. '2023csb1122' → '2023CSB1122'
             '2023-CSB-1122' → '2023CSB1122'
             '2023 CSB 1122' → '2023CSB1122'
             'unknown' → None
        """
        if not raw or raw.lower() in ('unknown', 'none', 'n/a', ''):
            return None

        clean = raw.strip()

        # Try to match the pattern
        m = cls.ENTRY_NUMBER_PATTERN.search(clean)
        if m:
            year = m.group(1)
            branch = m.group(2).upper()
            number = m.group(3)
            return f"{year}{branch}{number}"

        # Fallback: just uppercase and strip spaces/hyphens
        fallback = re.sub(r'[\s\-_./]', '', clean).upper()
        if len(fallback) >= 6:
            return fallback

        return None

    # ──────────────────────────────────────
    #  Name Cross-Verification
    # ──────────────────────────────────────

    @staticmethod
    def _check_name_mismatch(
        sheet_name: str,
        ocr_name: str,
        entry_number: str,
        row: int
    ) -> Optional[Dict]:
        """
        Cross-verify names from the sheet and OCR.
        Returns a mismatch dict if names don't match, None otherwise.
        
        Matching rules:
        1. Exact match (case-insensitive) → OK
        2. Any shared word (first name or last name) → OK
        3. One name is a substring of the other → OK
        4. Otherwise → mismatch (but score is still written)
        """
        if not sheet_name or not ocr_name:
            return None  # Can't verify, skip

        s = sheet_name.strip().lower()
        o = ocr_name.strip().lower()

        if not s or not o or s == 'unknown' or o == 'unknown':
            return None

        # 1. Exact match
        if s == o:
            return None

        # 2. Shared words (first name / last name overlap)
        s_parts = set(s.split())
        o_parts = set(o.split())
        if s_parts.intersection(o_parts):
            return None

        # 3. Substring check (OCR might get partial name)
        if s in o or o in s:
            return None

        # 4. Check if any individual word from one appears in the other string
        for word in s_parts:
            if len(word) >= 3 and word in o:
                return None
        for word in o_parts:
            if len(word) >= 3 and word in s:
                return None

        # Mismatch — flag it but still write the score
        return {
            "entry_number": entry_number,
            "sheet_name": sheet_name,
            "ocr_name": ocr_name,
            "row": row,
            "score_written": True
        }

    # ──────────────────────────────────────
    #  Reading Student List
    # ──────────────────────────────────────

    def read_student_list(self, sheet_url: str) -> Dict:
        """
        Read the student list from a Google Sheet.
        
        Auto-detects columns for entry number, name, and marks.
        
        Returns:
            {
                "spreadsheet_id": "...",
                "sheet_name": "Sheet1",
                "columns": {
                    "entry_number": {"index": 0, "letter": "A", "header": "Entry Number"},
                    "name": {"index": 1, "letter": "B", "header": "Name"},
                    "marks": {"index": 2, "letter": "C", "header": "Marks"}
                },
                "students": [
                    {"row": 2, "entry_number": "2023CSB1122", "name": "Harsh", "marks": None},
                    ...
                ]
            }
        """
        if not self.service:
            raise RuntimeError("Sheets service not initialized. Check credentials.")

        spreadsheet_id, sheet_name = self.parse_sheet_url(sheet_url)

        # Get spreadsheet metadata to find sheet names
        spreadsheet = self.service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()

        sheets = spreadsheet.get('sheets', [])
        if not sheets:
            raise ValueError("Spreadsheet has no sheets")

        # Use first sheet if no specific sheet specified
        if not sheet_name:
            sheet_name = sheets[0]['properties']['title']

        # Read all data
        range_name = f"'{sheet_name}'"
        result = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()

        values = result.get('values', [])
        if not values or len(values) < 2:
            raise ValueError("Sheet is empty or has no data rows (need at least header + 1 row)")

        # Detect columns from header
        headers = values[0]
        columns = self._detect_columns(headers)

        if not columns.get('entry_number'):
            raise ValueError(
                f"Could not detect entry number column. "
                f"Headers found: {headers}. "
                f"Expected one of: {self.ENTRY_NUMBER_ALIASES}"
            )

        # Parse student rows
        students = []
        entry_col = columns['entry_number']['index']
        name_col = columns.get('name', {}).get('index')
        marks_col = columns.get('marks', {}).get('index')

        for row_idx, row in enumerate(values[1:], start=2):  # 1-indexed, skip header
            entry_number = self._safe_get(row, entry_col, '').strip()
            if not entry_number:
                continue  # Skip empty rows

            name = self._safe_get(row, name_col, '').strip() if name_col is not None else ''
            marks_raw = self._safe_get(row, marks_col, None) if marks_col is not None else None

            marks = None
            if marks_raw and str(marks_raw).strip():
                try:
                    marks = float(marks_raw)
                except (ValueError, TypeError):
                    marks = None

            students.append({
                "row": row_idx,
                "entry_number": entry_number,
                "name": name,
                "marks": marks,
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
        Match evaluated results to students by entry_number and write marks.
        
        Entry numbers are matched using normalized format (yyyyBBBnnnn).
        Names are cross-verified — mismatches are flagged but marks are still written.
        """
        if not self.service:
            raise RuntimeError("Sheets service not initialized. Check credentials.")

        # Read current state
        sheet_data = self.read_student_list(sheet_url)
        spreadsheet_id = sheet_data['spreadsheet_id']
        sheet_name = sheet_data['sheet_name']
        columns = sheet_data['columns']
        students = sheet_data['students']

        if not columns.get('marks'):
            raise ValueError(
                "No 'marks' column detected in the sheet. "
                "Please add a column header like 'Marks', 'Score', or 'Total'."
            )

        marks_col_letter = columns['marks']['letter']

        # Build lookup: normalized_entry → result
        results_map = {}
        results_original = {}  # normalized → original string
        for r in results:
            raw = str(r.get('entry_number', '')).strip()
            normalized = self._normalize_entry_number(raw)
            if normalized:
                results_map[normalized] = r
                results_original[normalized] = raw

        print(f"📊 Results to match ({len(results_map)} entries):")
        for k, v in list(results_map.items())[:10]:
            print(f"    {results_original[k]} → normalized: {k}")

        # Match and prepare updates
        summary = {
            "updated": 0,
            "not_found_in_sheet": [],
            "not_found_in_results": [],
            "name_mismatches": [],
            "errors": [],
        }

        batch_data = []
        matched_normalized = set()

        for student in students:
            raw_entry = student['entry_number']
            normalized = self._normalize_entry_number(raw_entry)

            if not normalized:
                continue

            if normalized in results_map:
                matched_normalized.add(normalized)
                result = results_map[normalized]
                score = result.get('total_score', 0)

                # Cross-verify name
                mismatch = self._check_name_mismatch(
                    student.get('name', ''),
                    result.get('name', ''),
                    raw_entry,
                    student['row']
                )
                if mismatch:
                    summary['name_mismatches'].append(mismatch)

                # Prepare batch update
                cell_range = f"'{sheet_name}'!{marks_col_letter}{student['row']}"
                batch_data.append({
                    "range": cell_range,
                    "values": [[score]]
                })
                print(f"  ✅ Matched: {raw_entry} (→{normalized}) → score {score}")
            else:
                summary['not_found_in_results'].append(raw_entry)

        # Find entries in results but not in sheet
        for norm in results_map:
            if norm not in matched_normalized:
                summary['not_found_in_sheet'].append(results_original.get(norm, norm))

        # Execute batch update
        if batch_data:
            try:
                body = {
                    "valueInputOption": "RAW",
                    "data": batch_data,
                }
                self.service.spreadsheets().values().batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body=body
                ).execute()
                summary['updated'] = len(batch_data)
                print(f"✅ Updated {len(batch_data)} rows in Google Sheet")
            except Exception as e:
                summary['errors'].append(f"Batch update failed: {str(e)}")
                print(f"❌ Batch update failed: {e}")

        if summary['not_found_in_results']:
            print(f"⚠️  {len(summary['not_found_in_results'])} sheet students had no matching result")
        if summary['not_found_in_sheet']:
            print(f"⚠️  {len(summary['not_found_in_sheet'])} results had no matching sheet entry")
        if summary['name_mismatches']:
            print(f"⚠️  {len(summary['name_mismatches'])} name mismatches detected:")
            for m in summary['name_mismatches']:
                print(f"     {m['entry_number']}: sheet='{m['sheet_name']}' vs ocr='{m['ocr_name']}'")

        return summary

    # ──────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────

    def _detect_columns(self, headers: List[str]) -> Dict:
        """
        Auto-detect which columns contain entry_number, name, and marks
        based on header text matching.
        """
        columns = {}
        normalized_headers = [h.strip().lower() for h in headers]

        for idx, header in enumerate(normalized_headers):
            col_letter = self._index_to_letter(idx)

            if not columns.get('entry_number'):
                if header in self.ENTRY_NUMBER_ALIASES or any(alias in header for alias in self.ENTRY_NUMBER_ALIASES):
                    columns['entry_number'] = {
                        "index": idx,
                        "letter": col_letter,
                        "header": headers[idx]
                    }

            if not columns.get('name'):
                if header in self.NAME_ALIASES or any(alias in header for alias in self.NAME_ALIASES):
                    columns['name'] = {
                        "index": idx,
                        "letter": col_letter,
                        "header": headers[idx]
                    }

            if not columns.get('marks'):
                if header in self.MARKS_ALIASES or any(alias in header for alias in self.MARKS_ALIASES):
                    columns['marks'] = {
                        "index": idx,
                        "letter": col_letter,
                        "header": headers[idx]
                    }

        return columns

    @staticmethod
    def _index_to_letter(index: int) -> str:
        """Convert 0-based column index to spreadsheet column letter (A, B, ..., Z, AA, ...)."""
        result = ""
        while True:
            result = chr(65 + (index % 26)) + result
            index = index // 26 - 1
            if index < 0:
                break
        return result

    @staticmethod
    def _safe_get(lst: list, idx: Optional[int], default=None):
        """Safely get an element from a list by index."""
        if idx is None or idx >= len(lst):
            return default
        return lst[idx]
