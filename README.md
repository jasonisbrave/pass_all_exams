<p align="right">
  <strong>EN</strong> | <a href="./README.zh-CN.md">简体中文</a>
</p>

<p align="center">
  <img src="docs/hero.svg" alt="Pass All Exams" width="760" />
</p>

<h1 align="center">Pass All Exams</h1>

<p align="center">
  <strong>An evidence-grounded Agent Skill for course exams and finals, spanning humanities, business, quantitative, programming, language, and memorization-heavy courses.</strong>
</p>

<p align="center">
  Turn notes, syllabi, past papers, and teacher priorities into a focused loop of mapping, teaching, retrieval, mistake repair, and spaced review.
</p>

<p align="center">
  Runs in Codex, Claude Code, OpenClaw, and OpenCode. <a href="#installation">Install the skill</a>, then start with <code>/exam &lt;course&gt; start</code>.
</p>

<p align="center">
  <a href="./CHANGELOG.md"><img src="https://img.shields.io/badge/version-3.1.0-2563EB?style=flat-square&amp;labelColor=111827" alt="Version 3.1.0" /></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-MIT-16A34A?style=flat-square&amp;labelColor=111827" alt="MIT license" /></a>
  <img src="https://img.shields.io/badge/Codex-supported-2563EB?style=flat-square&amp;labelColor=111827" alt="Codex supported" />
  <img src="https://img.shields.io/badge/Claude%20Code-supported-D97706?style=flat-square&amp;labelColor=111827" alt="Claude Code supported" />
  <img src="https://img.shields.io/badge/OpenClaw-supported-0F766E?style=flat-square&amp;labelColor=111827" alt="OpenClaw supported" />
  <img src="https://img.shields.io/badge/OpenCode-supported-9333EA?style=flat-square&amp;labelColor=111827" alt="OpenCode supported" />
</p>

## Contents

- [Overview](#overview) · [Why Pass All Exams](#why-pass-all-exams) · [Compatible Agents](#compatible-agents)
- [Installation](#installation) · [Quick Start](#quick-start) · [Review Loop](#review-loop) · [Evidence Contract](#evidence-contract) · [Commands](#commands)
- [Token Modes](#token-modes) · [Supported Course Types](#supported-course-types) · [Local State and CLI](#local-state-and-cli)
- [Build and Validate](#build-and-validate) · [Repository Layout](#repository-layout) · [Privacy](#privacy) · [Acknowledgments](#acknowledgments) · [License](#license)

## Overview

Pass All Exams is for students who need a practical review system, not another long pile of notes. Each session stays deliberately small:

```text
one course -> one high-yield point -> one explanation -> one retrieval question -> one repair or review card
```

The workflow is divided into focused components:

| Component | Responsibility |
|---|---|
| [`SKILL.md`](./SKILL.md) | Lightweight agent-facing entry point. |
| [`references/`](./references/) | Detailed stage rules, loaded only when needed. |
| [`scripts/examctl.py`](./scripts/examctl.py) | Deterministic local course state and progress records. |
| [`scripts/ingest_materials.py`](./scripts/ingest_materials.py) | Material conversion and indexing with Microsoft MarkItDown. |
| [`scripts/install.sh`](./scripts/install.sh) and [`scripts/quick-install.sh`](./scripts/quick-install.sh) | Installation across supported agents. |
| [`scripts/package_skill.py`](./scripts/package_skill.py) | Uploadable `.skill` archive creation. |

## Why Pass All Exams

| Common review problem | How the skill responds |
|---|---|
| The model writes long notes but never checks recall. | Every taught point is followed by a retrieval step. |
| Exam predictions sound teacher-confirmed when they are not. | Responses distinguish source-backed material, reasonable inference, and items needing confirmation. |
| Chat history becomes expensive to reread. | Progress lives in `state.json`, `errors.jsonl`, and `cards.jsonl`. |
| Cram tools often fit only humanities courses. | The pipeline includes qualitative, quantitative, programming, language, and memorization-heavy patterns. |
| Mistakes are re-explained in the same words. | Errors are classified, repaired with a new representation, and retested from a new angle. |

## Compatible Agents

Pass All Exams runs inside agent tools that can load a folder containing `SKILL.md` and follow its reusable workflow. You need one compatible agent; no knowledge of Agent Skill internals is required.

| Agent | What it is | Official resource |
|---|---|---|
| Codex | OpenAI's coding agent, available through ChatGPT and local developer workflows. | [openai.com/codex](https://openai.com/codex/) |
| Claude Code | Anthropic's agentic coding tool. Personal skills use `~/.claude/skills`; project skills use `.claude/skills`. | [Claude Code documentation](https://code.claude.com/docs/en/overview) |
| OpenClaw | An open agent platform with a skill system built around `SKILL.md`. | [OpenClaw documentation](https://docs.openclaw.ai/) |
| OpenCode | A coding agent that discovers project and global Agent Skills. | [OpenCode documentation](https://opencode.ai/docs/) |

## Installation

The repository name is `pass_all_exams`; the installed skill name is `pass-all-exams`. Run the installer commands below in Bash.

### Option 1: One-Click Install (Recommended)

The quick installer clones the project, installs the MarkItDown file-conversion dependencies, and copies the skill into the selected agent directory:

```bash
curl -fsSL https://raw.githubusercontent.com/jasonisbrave/pass_all_exams/main/scripts/quick-install.sh | bash -s -- <agent>
```

Replace `<agent>` with one of these supported values:

| Agent | Scope | `<agent>` value |
|---|---|---|
| Codex | Global, or under `CODEX_HOME` when set | `codex` |
| Claude Code | Global | `claude` |
| Claude Code | Current project only | `claude-project` |
| OpenClaw | Global | `openclaw` |
| OpenCode | Global | `opencode` |
| OpenCode | Current project only | `opencode-project` |

To skip automatic Python dependency installation, place `--skip-deps` before the agent value:

```bash
curl -fsSL https://raw.githubusercontent.com/jasonisbrave/pass_all_exams/main/scripts/quick-install.sh | bash -s -- --skip-deps <agent>
```

### Option 2: Install from Git

Clone the repository and enter its root directory:

```bash
git clone https://github.com/jasonisbrave/pass_all_exams.git
cd pass_all_exams
```

If you plan to convert course files, install the optional dependency set:

```bash
python3 -m pip install -r requirements-markitdown.txt
```

Then run the installer for your agent:

| Agent | Scope | Command |
|---|---|---|
| Codex | Global, or under `CODEX_HOME` when set | `bash scripts/install.sh codex` |
| Claude Code | Global | `bash scripts/install.sh claude` |
| Claude Code | Current project only | `bash scripts/install.sh claude-project` |
| OpenClaw | Global | `bash scripts/install.sh openclaw` |
| OpenCode | Global | `bash scripts/install.sh opencode` |
| OpenCode | Current project only | `bash scripts/install.sh opencode-project` |

For project-local installation, run the command from the root of the project that should receive the skill.

### Option 3: Clone Directly into a Skill Directory

```bash
# Codex
git clone https://github.com/jasonisbrave/pass_all_exams.git ~/.codex/skills/pass-all-exams

# Codex with CODEX_HOME
git clone https://github.com/jasonisbrave/pass_all_exams.git "$CODEX_HOME/skills/pass-all-exams"

# Claude Code, global
git clone https://github.com/jasonisbrave/pass_all_exams.git ~/.claude/skills/pass-all-exams

# Claude Code, project-local
git clone https://github.com/jasonisbrave/pass_all_exams.git .claude/skills/pass-all-exams

# OpenClaw
git clone https://github.com/jasonisbrave/pass_all_exams.git ~/.openclaw/skills/pass-all-exams

# OpenCode, global
git clone https://github.com/jasonisbrave/pass_all_exams.git ~/.config/opencode/skill/pass-all-exams

# OpenCode, project-local
git clone https://github.com/jasonisbrave/pass_all_exams.git .opencode/skill/pass-all-exams
```

If your agent accepts uploaded skill archives, you can also [build a `.skill` package locally](#build-and-validate).

## Quick Start

After installation, ask the agent to start a course:

```text
/exam Organizational Behavior start
```

Or provide the context you already have in natural language:

```text
Use pass-all-exams to help me review Organizational Behavior.
The exam has multiple choice, short answer, and case analysis.
My must-know topics are Hawthorne studies and expectancy theory.
```

Chinese courses work in the same way:

```text
/exam 组织行为学 start
```

```text
帮我用 pass-all-exams 复习组织行为学。
考试题型是选择题、简答题和案例分析。
老师强调必考：霍桑实验、期望理论。我会继续粘贴课堂笔记。
```

To include course files, run the ingestion script from the repository root or installed skill directory:

```bash
python3 scripts/ingest_materials.py \
  --course "Organizational Behavior" \
  ~/Downloads/syllabus.pdf \
  ~/Downloads/week-1-slides.pptx \
  ~/Downloads/review-notes.docx
```

The converted Markdown is saved in the course's local `materials/` directory and reused by later stages.

## Review Loop

| Stage | What happens |
|---|---|
| **Intake** | Collect the course, exam date or time budget, question types, materials, and must-know points. |
| **Ingest** | Convert uploaded files to Markdown with Microsoft MarkItDown and cache converted materials by SHA-256. |
| **Map** | Split materials into exam-sized points and mark source confidence. |
| **Teach** | Explain one point concrete-first, in at most three chunks, with one self-generation prompt. |
| **Drill** | Practise using the real exam types: choice, case analysis, calculation, code tracing, short answer, and others. |
| **Diagnose and repair** | Classify the miss, switch representation, and retest from a new angle instead of repeating the explanation. |
| **Review** | Create same-day, next-day, three-day, and final-day retrieval cards. |

## Evidence Contract

Every substantive explanation, exam prediction, or grading response should make its source status visible:

| Label | Meaning |
|---|---|
| **Source-backed** | Directly supported by notes, syllabi, teacher wording, past papers, or pasted material. |
| **Reasonable inference** | A useful exam-preparation inference based on standard course knowledge and common assessment patterns. |
| **Needs confirmation** | Something that depends on the teacher, textbook edition, or local exam scope and still needs checking. |

This is the main hallucination-control layer. Without materials, the skill uses general-knowledge mode and must not pretend to know the teacher's actual exam scope; provide a syllabus or point list before relying on high-stakes predictions.

## Commands

These commands are prompts interpreted by the agent, not standalone shell commands.

| Command | Use |
|---|---|
| `/exam <course> start` | Create or refresh a course plan. |
| `/cram <course> start` | Alias for cram-style workflows. |
| `/exam <course> resume` | Continue from saved progress and recent JSONL records. |
| `/exam <course> drill` | Retrieve current weak points and practise due material. |
| `/exam <course> retry <point>` | Reteach and retest a weak point, resolve the selected error, and log the session. |
| `/exam <course> summary` | Produce a final-day checklist. |

## Token Modes

| Mode | Best for | Behavior |
|---|---|---|
| `compact` | Most cram sessions | One point, one example, one question, and one correction. |
| `standard` | Normal weekly review | Adds one example and a relation to a prior point. |
| `deep` | Hard subjects or high-stakes finals | Adds derivation, edge cases, and mixed practice. |

The default is `compact`. Progressive disclosure keeps `SKILL.md` short: detailed rules in `references/` are loaded only when needed.

## Supported Course Types

| Course type | Examples | Special handling |
|---|---|---|
| Humanities and social sciences | Law, politics, sociology, education | Definitions, comparisons, and case-analysis scoring structures |
| Business and management | Organizational behavior, marketing, accounting theory | Frameworks, traps, and case application |
| Quantitative courses | Calculus, statistics, economics methods | Formula conditions, worked examples, and calculation-error diagnosis |
| Programming courses | Data structures, databases, operating systems, Python/C/Java | Trace questions, bug repair, and complexity explanations |
| Language and memorization-heavy courses | English, history, medicine basics | Cloze exercises, recall cards, and contrast tables |

## Local State and CLI

Run the Python commands in this section from the repository root or installed skill directory.

### Storage and Files

By default, active and archived courses are stored at:

```text
~/.pass-all-exams/courses/<course-slug>/
~/.pass-all-exams/archive/<course-slug>/
```

`examctl.py` supports three ways to select storage:

- Set `PASS_ALL_EXAMS_HOME` to override the data home; courses live under `<data-home>/courses`.
- Pass `--data-home <dir>` to select `<dir>/courses`. It overrides the environment variable and is accepted before or after the subcommand.
- Pass `--root <courses-dir>` to name the directory that directly contains course folders. It takes precedence over `--data-home` and is also accepted before or after the subcommand. Do not pass the data home itself to `--root`.

For ingestion with custom storage, pass the same courses directory to `ingest_materials.py --root <courses-dir>`.

Within `examctl.py`, only `init` creates a course. Its other subcommands require an existing course directory and `state.json`; missing state produces a clear error with exit code 2 instead of silently creating files.

Each course can contain:

| File or directory | Purpose |
|---|---|
| `course.yaml` | Course profile: exam types, materials, must-know points, and preferences. |
| `state.json` | Current stage, point-level status, and counts. |
| `materials/` | Markdown files converted by MarkItDown. |
| `materials.jsonl` | Material index: source path, SHA-256, output path, title, byte count, and status. |
| `errors.jsonl` | Wrong answers, diagnoses, and repair history. |
| `cards.jsonl` | Retrieval cards and due dates. |
| `sessions.jsonl` | Session log appended by `log-session`. |

### Course and Session Commands

Create a course, inspect progress, or print a summary:

```bash
python3 scripts/examctl.py init --course "Organizational Behavior"
python3 scripts/examctl.py status --course "Organizational Behavior"
python3 scripts/examctl.py summary --course "Organizational Behavior"
```

Log a session without changing point status:

```bash
python3 scripts/examctl.py log-session \
  --course "Organizational Behavior" \
  --action drill \
  --topic "Expectancy theory" \
  --result pass \
  --errors-corrected 1 \
  --cards-added 2
```

Resolve the latest matching open or stubborn error and record the repair:

```bash
python3 scripts/examctl.py resolve-error \
  --course "Organizational Behavior" \
  --point "Expectancy theory" \
  --repair "Retaught with a contrast table and retested with a new scenario"

# Optional filters: --contains "confusion", --date 2026-11-15,
# or --index N for a 1-based line number in errors.jsonl.
```

Archive a completed course or restore it later. Both operations move the whole directory without deleting data and refuse to overwrite an existing target:

```bash
python3 scripts/examctl.py archive-course \
  --course "Organizational Behavior" \
  --reason "Course completed"
python3 scripts/examctl.py restore-course --course "Organizational Behavior"
```

### Record Progress and Errors

Record a taught point:

```bash
python3 scripts/examctl.py record-point \
  --course "Organizational Behavior" \
  --point "Expectancy theory" \
  --level must \
  --status taught \
  --source material
```

Optionally record mastery evidence and a review date:

```bash
python3 scripts/examctl.py record-point \
  --course "Organizational Behavior" \
  --point "Expectancy theory" \
  --status mastered \
  --verification "Passed a retrieval question without notes" \
  --review-due 2026-12-20
```

Record an error:

```bash
python3 scripts/examctl.py record-error \
  --course "Organizational Behavior" \
  --point "Expectancy theory" \
  --reason confusion \
  --question-type "multiple choice" \
  --must-know
```

### Material Ingestion

Microsoft [MarkItDown](https://github.com/microsoft/markitdown) converts PDF, Word, PowerPoint, Excel, images, audio, HTML, CSV, JSON, XML, ZIP, EPub, and other supported formats into Markdown before the study loop uses them.

```bash
python3 scripts/ingest_materials.py \
  --course "Organizational Behavior" \
  ~/Downloads/syllabus.pdf
```

By default, ingestion accepts local files only. Trusted HTTP(S) URLs require `--allow-url` because MarkItDown reads resources with the current process's privileges. Audio transcription may require system audio tooling such as `ffmpeg`; ordinary PDF, Office, and text conversion does not.

## Build and Validate

From the repository root, create an uploadable `.skill` archive:

```bash
python3 scripts/package_skill.py
```

The default output is `dist/pass-all-exams.skill`. Use this file with an agent or interface that supports uploaded skill archives.

Validate the package layout and compile the Python scripts:

```bash
python3 scripts/validate_skill.py
python3 -m py_compile scripts/examctl.py scripts/ingest_materials.py scripts/validate_skill.py scripts/package_skill.py
```

## Repository Layout

```text
pass_all_exams/
├── SKILL.md                     # Agent-facing entry point
├── README.md                    # English documentation
├── README.zh-CN.md              # Chinese documentation
├── CHANGELOG.md                 # Release history
├── PROJECT_CHECK.md             # Validation record
├── LICENSE                      # MIT license
├── requirements-markitdown.txt  # MarkItDown dependency set
├── agents/
│   └── openai.yaml              # Codex UI metadata
├── configs/
│   └── example.yaml             # Sample course profile
├── docs/
│   └── hero.svg                 # README artwork
├── references/
│   ├── pipeline.md              # Detailed review workflow
│   ├── prompt-patterns.md       # Reusable prompt shapes
│   ├── platforms.md             # Agent installation notes
│   └── comparison.md            # Design comparison notes
├── scripts/
│   ├── examctl.py               # Local course state helper
│   ├── ingest_materials.py      # MarkItDown ingestion helper
│   ├── install.sh               # Agent install helper
│   ├── quick-install.sh         # One-click installer
│   ├── package_skill.py         # .skill archive builder
│   └── validate_skill.py        # Package layout validator
└── tests/
    └── test_examctl.py          # Standard-library unittest suite
```

## Privacy

Course state is stored locally by default. The skill does not require its own external service, database, or account; notes, errors, and review cards remain under the selected data home unless you move or share them. Review your agent's and MarkItDown's settings before processing sensitive materials.

## Acknowledgments

This project uses [Microsoft MarkItDown](https://github.com/microsoft/markitdown) to turn course materials into Markdown for the study pipeline. MarkItDown is developed and maintained by Microsoft.

## License

[MIT](./LICENSE)
