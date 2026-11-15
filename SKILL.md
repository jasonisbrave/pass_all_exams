---
name: pass-all-exams
description: Use for Chinese/bilingual exam prep, material ingestion, cram sessions, mock tests, wrong-answer remediation, spaced review, error resolution, safe course archival, or /exam and /cram. Turn materials, syllabi, teacher重点, past papers, and exam types into an evidence-grounded study loop for Codex, Claude Code, OpenClaw, and OpenCode.
version: 3.1.0
license: MIT
compatibility: codex, claude-code, openclaw, opencode
metadata:
  openclaw:
    requires:
      bins:
        - python3
    emoji: "🎓"
    homepage: "https://github.com/jasonisbrave/pass_all_exams"
---

# Pass All Exams

Evidence-grounded exam sessions with progress, spaced review, and safe state lifecycle.

## Commands

- `/exam <course> start` or `/cram <course> start`: create or refresh a plan.
- `/exam <course> resume`: continue from `state.json` and JSONL tails.
- `/exam <course> drill`: retrieve current weak points.
- `/exam <course> retry <point>`: reteach, retest, resolve the selected error, and log the session.
- `/exam <course> summary`: produce a final-day checklist.

## First Move

For a new course, collect only missing: exam date/format, materials/syllabus, must-know points, and compact/standard/deep mode.

```bash
python3 scripts/examctl.py init --course "<course>"
python3 scripts/ingest_materials.py --course "<course>" "<file1>" "<file2>"
```

Default state: `~/.pass-all-exams/courses/<slug>/`. `PASS_ALL_EXAMS_HOME` overrides the data home; `--data-home DIR` selects `DIR/courses`; `--root` is the courses directory itself. Only `init` creates a course; every other `examctl` command rejects missing course/state without creating files.

Read converted materials under `<course>/materials/` instead of reparsing original uploads.

## Core Loop

Run one narrow stage at a time:

1. **Map**: split materials into exam-sized points and mark source confidence.
2. **Teach**: concrete-first, <=3 chunks, one self-generation prompt.
3. **Drill**: use actual exam types, active recall, interleaving, and traps.
4. **Diagnose**: classify confusion, missing term, logic reversal, or transfer failure.
5. **Repair**: switch method and retest with a new angle; do not repeat the same explanation.
6. **Review**: use same-day/next-day/3-day/final-day retrieval per `references/pipeline.md`.

## State Lifecycle: Use CLI, Not Hand Edits

```bash
python3 scripts/examctl.py status --course "<course>"
python3 scripts/examctl.py record-point --course "<course>" --point "<point>" --level must --status mastered --source material --verification "<actual validation>" --review-due YYYY-MM-DD
python3 scripts/examctl.py resolve-error --course "<course>" --point "<point>" --repair "<new-angle retest evidence>"
python3 scripts/examctl.py log-session --course "<course>" --action retry --topic "<point>" --result "<outcome>" --quiz "<actual check>" --note "<next>"
```

`resolve-error` selects the latest matching open/stubborn row, or an exact `--index N`; it writes `corrected/corrected_at/repair` and recomputes error counts. `log-session` appends without changing point status. Keep counts synchronized with records. Full filters and flags: `README.zh-CN.md`.

## Mastery and Repair

- Same-day correction is repair evidence, not proof of durable mastery.
- Mark `mastered` only after the course's declared validation fully passes; record `verification/review_due` when possible.
- If an anchor fails again later, in mixed chapters, or in timed output, record recurrence and mark the error `stubborn`; use existing point-status conventions, not a parallel schema.
- Continue delayed and mixed retrieval after correction. Do not replace the existing review schedule with an unreviewed one.

**🔴 CHECKPOINT · STOP**: Before changing real progress, bulk-editing JSONL, archiving a course, or running an experiment, state the change and obtain user confirmation. Test with temporary `PASS_ALL_EXAMS_HOME`, never the real course store.

## Archive and Restore

Archive rather than delete completed, suspended, or deferred courses:

```bash
python3 scripts/examctl.py archive-course --course "<course>" --reason "<reason>"
python3 scripts/examctl.py restore-course --course "<course>"
```

Archive moves `courses/<slug>/` intact to `<data-home>/archive/<slug>/` and records reason/date; restore moves it back. Both refuse to overwrite. Document reason, material locations, progress snapshot, and restore path in archive README and update active-course guides.

## Failure Handling and Blacklist

| Trigger | Required response |
|---|---|
| Missing course/state | Stop; init only when a new course is intended |
| No matching unresolved error | Inspect/change filters; never add a fake error to refresh counts |
| Repeated miss after correction | Diagnose, mark stubborn, schedule delayed/mixed retrieval |
| Archive target exists | Stop and preserve source and target |
| Tests unavailable | Mark `dry_run`; do not claim full validation |

**Do not** overwrite learning history, master from one immediate answer, silently create a course on a typo, invent a parallel status taxonomy, experiment on real progress, or keep a change only because an absolute judge score increased.

## Anti-Hallucination Contract

Every substantive teaching or answer-checking response separates:
- `资料依据`: directly supported by user materials.
- `合理推断`: useful inference from standard knowledge.
- `待确认`: facts requiring the teacher, textbook, or notes.

Without materials, declare general-knowledge mode and ask for a syllabus or point list before high-stakes predictions.

## Token Budget Rules

- Default `compact`: one point, example, question, correction.
- Load only the needed reference; prefer tables and JSONL over chat history.
- Summarize prior work from `state.json`, `cards.jsonl`, and `errors.jsonl`.

Use `references/prompt-patterns.md` for prompts and `references/platforms.md` for installation.
