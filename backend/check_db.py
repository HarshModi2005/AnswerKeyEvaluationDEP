import sqlite3
import os

db_path = "e:/Projects/AnswerKeyEvaluationDEP/backend/evaluation.db"

if not os.path.exists(db_path):
    print(f"Database file not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM users")
        rows = c.fetchall()
        if not rows:
            print("No users found in the database.")
        for row in rows:
            d = dict(row)
            print(f"Email: {d['email']} | Password: '{d['password']}' | Role: {d['role']}")

    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
    finally:
        conn.close()
