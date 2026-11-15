# Project Check

## 3.1.0 - 2026-11-16

Environment used for reliability-update validation:

- Windows, Python 3.14 (`C:\Python314`)
- Repository: standalone fork workspace, uncommitted changes

Checks completed (all commands run from the repo root):

- `python -m unittest discover -s tests -v` passed: 32 tests, all OK (covers env/`--data-home` resolution including after-subcommand placement and `--root` precedence, non-init refusal without directory creation, resolve-error latest/index/no-match/stubborn counts, log-session fields and state date, archive/restore roundtrip and no-overwrite refusals, record-point verification/review-due plus invalid-date rejection, and the legacy init/record-error/add-card/status/summary flow).
- `python -m py_compile scripts/examctl.py scripts/ingest_materials.py scripts/validate_skill.py scripts/package_skill.py tests/test_examctl.py` passed. (The literal `scripts/*.py` form does not glob on Windows PowerShell and must be expanded.)
- `python scripts/validate_skill.py` passed: "OK: pass-all-exams skill package is valid".
- `git diff --check` passed (only a benign LF→CRLF autocrlf warning for `scripts/examctl.py`, no whitespace errors).

Manual end-to-end smoke (temp data home, Chinese course name, all new commands):

- `init` → `record-error --stubborn` → `log-session` → `resolve-error` (printed `index: 1`, `status: corrected`, `corrected_at`, `repair`) → `archive-course` (moved to `<data>/archive/`) → `status` after archive failed with exit 2 and created nothing → `restore-course` (moved back) → `summary` showed 错题记录 1 / 顽固点 0.
- Refusing behavior verified: `status` on a missing course exited 2 with "course not found" and no directory was created.

Manual spot checks behind the tests:

- A course passed to `--root` as a data home lands directly under that dir (documented behavior), confirming the help-text warning is accurate.
- An ambient `PASS_ALL_EXAMS_HOME` set in the parent session was correctly ignored by subprocess tests via environment isolation, and honored when explicitly set.

Final orchestrator verification on 2026-11-16:

- Re-ran all 32 unit tests, script/test compilation, `validate_skill.py`, and `git diff --check`: all passed.
- Built `dist/pass-all-exams.skill`; 21 package entries, zero `tests/` or `experiments/` artifacts, embedded SKILL.md version 3.1.0 verified.
- Darwin paired review: three independent judges all returned `better / clear`; nonblocking wording notes are retained in `experiments/darwin/paired-2026-11-16.md`.

## 3.0.0 - 2026-08-14

Release validation:

- Version metadata and release links were synchronized for v3.0.0.
- `python3 scripts/validate_skill.py` passed.
- `python3 -m py_compile scripts/examctl.py scripts/ingest_materials.py scripts/validate_skill.py scripts/package_skill.py` passed.
- `git diff --check` passed.
- `.skill` package was rebuilt and its embedded `SKILL.md` version was verified as 3.0.0.

## 2.0.0 - 2026-06-08

Environment used for MarkItDown validation:

- Python: 3.12.13
- MarkItDown: 0.1.6, installed through `requirements-markitdown.txt`
- Temporary venv: `/tmp/pass-all-exams-v2-venv`

Checks completed:

- `python3 scripts/validate_skill.py` passed.
- `python3 -m py_compile scripts/examctl.py scripts/ingest_materials.py scripts/validate_skill.py scripts/package_skill.py` passed.
- `git diff --check` passed.
- `python3 -m pip install -r requirements-markitdown.txt` passed in a clean temporary virtual environment.
- `scripts/ingest_materials.py` converted a local Markdown course file into `materials/<name>-<sha>.md`.
- `materials.jsonl` recorded source path, SHA-256 hash, output path, title, byte count, and conversion status.
- `state.json` updated `counts.materials`.
- Re-ingesting the same unchanged file returned `status: cached`.
- URL ingestion was rejected by default and required explicit `--allow-url`.
- `.skill` package was rebuilt with the v2.0.0 files.

Known operational note:

- Audio transcription can require system audio tooling such as `ffmpeg`. This does not affect ordinary PDF, Office, HTML, CSV/JSON/XML, or text conversion.
