# CourseFlow homework — Search & Register

You already saw the trainee list and the 60-day renewal indicator. Now **you** extend the same system.

## Required feature A: Search courses (GET)
- Support `GET /api/trainees?course=refresher`.
- Match by substring, case-insensitively (for example `refresher` matches `Security Refresher`).
- `GET /api/trainees` without the filter must still return all trainees.
- Add a simple course search box or dropdown in the webpage.
- Empty search should show all trainees.

## Required feature B: Register a fictional trainee (POST)
- Support `POST /api/trainees` with JSON: `name`, `course`, `expires_on`.
- `name` and `course` must be nonempty after trimming spaces.
- `expires_on` may be null or a valid date in `YYYY-MM-DD` format.
- Save accepted data to SQLite; do not only change a temporary list in memory.
- Return HTTP `201 Created` with the created record including an ID.
- Return HTTP `400 Bad Request` for missing/invalid fields or invalid JSON.
- Add a small registration form on the webpage; display new records after submission.
- Preserve the existing renewal badge.

## Required testing
1. No filter returns all records.
2. Case-insensitive substring filter returns only matching courses.
3. Unknown course returns an empty list, not an error.
4. Valid POST returns 201 and a generated ID.
5. A saved trainee appears in a later GET (persists across browser refresh).
6. Empty name is rejected with 400.
7. Invalid expiry date is rejected with 400.
8. The original renewal-rule tests still pass.

Write at least 4 **new automated tests** and perform at least 3 manual checks. Keep tests independent of the main app database. Record test results in TEST_RESULTS.md.

## Scope
Do not add accounts, login, cloud deployment, an LLM, RAG, or an agent. This is a software foundations task.

## Evidence to submit
- Files or GitHub repository link (optional if not comfortable with Git yet)
- `TEST_RESULTS.md` with command, passed/failed counts and one issue you fixed
- Two screenshots: one filtered course list, one successful registration
- A 5–8 sentence explanation of frontend, API, database, GET, POST, and testing

Helpful starting command: `python server.py`
Run tests: `python -m unittest discover -s tests -v`
