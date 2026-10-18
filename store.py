from pathlib import Path
from datetime import date, timedelta
from contextlib import closing
import sqlite3

DB = Path(__file__).resolve().parent / 'courseflow.sqlite3'

def initialize():
    # closing() closes the file when done; "conn" alone only commits, which left the file locked on Windows
    with closing(sqlite3.connect(DB)) as conn, conn:
        conn.execute('CREATE TABLE IF NOT EXISTS trainees (id INTEGER PRIMARY KEY, name TEXT NOT NULL, course TEXT NOT NULL, expires_on TEXT)')
        n = conn.execute('SELECT COUNT(*) FROM trainees').fetchone()[0]
        if n == 0:
            today = date.today()
            samples = [
                (1, 'Alex Tan', 'Security Refresher', (today+timedelta(days=25)).isoformat()),
                (2, 'Mei Lim', 'Incident Reporting', (today+timedelta(days=140)).isoformat()),
                (3, 'Noor Ahmad', 'Site Operations', (today+timedelta(days=60)).isoformat()),
                (4, 'Jamie Wong', 'Access Control', None),
                (5, 'Priya Shah', 'Security Refresher', (today+timedelta(days=90)).isoformat()),
            ]
            conn.executemany('INSERT INTO trainees VALUES (?, ?, ?, ?)',samples)

def read_trainees(course=None):
    """All trainees, or only those whose course contains `course` (any letter case)."""
    sql = 'SELECT id, name, course, expires_on FROM trainees'
    params = []
    if course and course.strip():
        # instr() treats the search text literally, so % or _ are not wildcards
        sql += ' WHERE instr(lower(course), lower(?)) > 0'
        params.append(course.strip())
    with closing(sqlite3.connect(DB)) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(x) for x in conn.execute(sql + ' ORDER BY id', params)]

def read_courses():
    """Each course name in the trainees table once, in alphabetical order."""
    with closing(sqlite3.connect(DB)) as conn:
        return [row[0] for row in conn.execute('SELECT DISTINCT course FROM trainees ORDER BY course COLLATE NOCASE')]

def add_trainee(name, course, expires_on):
    """Save one already-validated trainee and return it with its new id."""
    with closing(sqlite3.connect(DB)) as conn, conn:
        cur = conn.execute('INSERT INTO trainees (name, course, expires_on) VALUES (?, ?, ?)', (name, course, expires_on))
        return {'id': cur.lastrowid, 'name': name, 'course': course, 'expires_on': expires_on}
