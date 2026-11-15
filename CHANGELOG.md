# Changelog

## 3.1.0 - 2026-11-16

- Restored `PASS_ALL_EXAMS_HOME` support in `scripts/examctl.py`: the data home defaults to the env var or `~/.pass-all-exams`, courses live under `<data-home>/courses`.
- Added a global `--data-home` option (accepted before or after the subcommand); kept `--root` with help text clarifying it points at the courses directory (not the data home).
- Non-`init` commands (record-point, record-error, add-card, status, summary, and the new commands) now require an existing course directory and `state.json`; they fail clearly instead of silently creating directories. Only `init` creates a course.
- Added `resolve-error`: marks the latest filtered open/stubborn error as `corrected` with `corrected_at` and a required `--repair` note, recomputes `counts.errors`/`counts.stubborn`, and prints the processed record with its 1-based `index`. Filters: `--point`, `--contains` (reason substring), `--date`, or direct selection via `--index`.
- Added `log-session`: appends one JSON line to `sessions.jsonl` with required `--course/--action/--topic/--result`, optional `--quiz/--note/--anki` and `--errors-corrected/--cards-added/--stubborn`; updates `state.updated_at` only.
- Added `archive-course` / `restore-course`: safely move whole course directories to/from `<courses-root>/../archive` (stamping/clearing `archived_at`/`archive_reason`); both refuse when the target already exists and never delete data.
- Added optional `--verification` and `--review-due` (ISO-validated) to `record-point`; existing invocations and the `points_done` rule are unchanged.
- Refactored count recomputation into shared helpers while keeping the JSON output and file formats backward compatible.
- Added a stdlib-only unittest suite `tests/test_examctl.py` (32 tests).
- Updated `SKILL.md` with the real state-lifecycle CLI, mastery/repair checkpoint, archive/restore workflow, failure handling, and blacklist; Darwin paired review voted 3/3 better (clear), and the user confirmed keep/publish at the final human checkpoint.

## 3.0.0 - 2026-08-14

- Synchronized the skill version metadata and release links for the v3.0.0 refresh.
- Rebuilt the uploadable `pass-all-exams.skill` package.

## 2.0.0 - 2026-06-08

- Added Microsoft MarkItDown-powered material ingestion for uploaded course files.
- Added `scripts/ingest_materials.py` to convert PDFs, Word documents, PowerPoint decks, spreadsheets, images, audio, HTML, CSV/JSON/XML, ZIP files, EPubs, and other MarkItDown-supported inputs into Markdown.
- Added local material storage under `~/.pass-all-exams/courses/<course-slug>/materials/`.
- Added `materials.jsonl` indexing with source path, SHA-256 hash, converted output path, title, byte count, and conversion status.
- Added hash-based caching so unchanged files are not converted repeatedly.
- Added `requirements-markitdown.txt` for installing the optional file-conversion dependency set.
- Updated README, Chinese README, SKILL instructions, and platform references for the file-upload workflow.

## 0.1.0 - 2026-06-07

- Initial portable Agent Skill for Codex, Claude Code, OpenClaw, and OpenCode.
- Added evidence-grounded exam-prep loop, local JSON/JSONL progress, review cards, install helper, package builder, and release archive.
