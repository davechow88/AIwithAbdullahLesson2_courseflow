# CourseFlow Homework Starter

A local educational website (Python standard-library server + SQLite + HTML/JavaScript) built with **fictional data only**. This is the same kind of app demonstrated in Lesson 2. It is intentionally **unfinished**: course filtering and trainee registration are your tasks.

## Setup (Windows)
1. Extract the ZIP. Open this folder in File Explorer.
2. Click the Explorer address bar, type `powershell`, press Enter.
3. Run `python --version` to verify Python is installed (3.10 or later).
4. Run `python server.py` and leave the terminal open.
5. Open `http://localhost:8765` for the website.
6. Open `http://localhost:8765/api/trainees` for the GET API.
7. Open another PowerShell window here and run `python -m unittest discover -s tests -v`.
8. Read **HOMEWORK_TASK.md** for acceptance criteria.

You may use Claude Code or Codex to inspect and work on the project, but **ask it to explain the plan first**. Verify every change.

## Project map
- `web/index.html`: webpage (frontend)
- `server.py`: local HTTP API (backend)
- `store.py`: database access and fake data
- `rules.py`: renewal calculation
- `scripts/api_healthcheck.py`: checks that a running server answers `GET /api/health` and `GET /api/trainees` (run `python scripts/api_healthcheck.py`)
- `tests/`: existing automated tests, which should keep passing
- `AGENTS.md`: guidance for Codex-compatible agents (not the program itself)
- `HOMEWORK_TASK.md`: the assignment
- `TEST_RESULTS_TEMPLATE.md`: copy to `TEST_RESULTS.md` and fill in

## Safety
Runs on `127.0.0.1` only. No authentication, role permissions or hardening. **Do not host publicly and do not use real trainee details.** `.gitignore` excludes SQLite databases and secrets.
