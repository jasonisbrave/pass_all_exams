#!/usr/bin/env python3
"""Deterministic state helper for pass-all-exams."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys
from pathlib import Path


def default_data_home() -> Path:
    env = os.environ.get("PASS_ALL_EXAMS_HOME")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".pass-all-exams"


DATA_HOME = default_data_home()
ROOT = DATA_HOME / "courses"


class CommandError(Exception):
    """User-facing command failure; main() turns it into exit code 2."""


def fail(message: str) -> None:
    raise CommandError(message)


def today() -> str:
    return dt.date.today().isoformat()


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff-]+", "", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "course"


def course_dir(course: str, root: Path = ROOT) -> Path:
    return root / slugify(course)


def archive_dir(root: Path = ROOT) -> Path:
    """Archive root sits next to the courses root: <data-home>/archive."""
    return Path(root).parent / "archive"


def courses_root_for(data_home: Path | None) -> Path:
    """Resolve the courses root from an explicit data home (or defaults)."""
    if data_home is not None:
        return Path(data_home).expanduser() / "courses"
    return default_data_home() / "courses"


def resolve_courses_root(args: argparse.Namespace) -> Path:
    """--root (explicit courses dir) wins; otherwise <data-home>/courses."""
    if getattr(args, "root", None) is not None:
        return Path(args.root).expanduser()
    return courses_root_for(getattr(args, "data_home", None))


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def append_jsonl(path: Path, item) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(item, ensure_ascii=False) + "\n")


def iter_jsonl(path: Path):
    if not path.exists():
        return iter(())
    return (json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def write_jsonl(path: Path, items) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in items),
        encoding="utf-8",
    )
    tmp.replace(path)


def ensure_course(course: str, root: Path = ROOT) -> Path:
    """Create the course skeleton. Only `init` may call this."""
    path = course_dir(course, root)
    path.mkdir(parents=True, exist_ok=True)
    return path


def require_course(course: str, root: Path) -> Path:
    """Return an existing course directory; never create anything."""
    path = course_dir(course, root)
    if not path.is_dir():
        fail(
            f"course not found: {path} "
            f"(nothing was created; run `examctl init --course \"{course}\"` first)"
        )
    state_path = path / "state.json"
    if not state_path.is_file():
        fail(
            f"course state missing: {state_path} "
            f"(nothing was created; run `examctl init --course \"{course}\"` first)"
        )
    return path


def refresh_point_counts(state: dict) -> None:
    points = state.setdefault("points", {})
    counts = state.setdefault("counts", {})
    counts["points_total"] = len(points)
    counts["points_done"] = sum(
        1 for item in points.values() if item.get("status") in {"taught", "corrected", "mastered"}
    )


def refresh_error_counts(state: dict, errors: list) -> None:
    counts = state.setdefault("counts", {})
    counts["errors"] = len(errors)
    counts["stubborn"] = sum(1 for item in errors if item.get("status") == "stubborn")


def refresh_card_counts(state: dict, cards: list) -> None:
    counts = state.setdefault("counts", {})
    counts["cards"] = len(cards)


def iso_date(value: str) -> str:
    """argparse type: strict ISO date (YYYY-MM-DD)."""
    try:
        return dt.date.fromisoformat(value).isoformat()
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected ISO date YYYY-MM-DD, got {value!r}")


def cmd_init(args) -> None:
    path = ensure_course(args.course, args.root)
    state_path = path / "state.json"
    if state_path.exists() and not args.force:
        print(f"exists: {path}")
        return

    today_s = today()
    state = {
        "course": args.course,
        "slug": path.name,
        "created_at": today_s,
        "updated_at": today_s,
        "mode": args.mode,
        "stage": "intake",
        "counts": {
            "points_total": 0,
            "points_done": 0,
            "errors": 0,
            "stubborn": 0,
            "cards": 0,
            "materials": 0,
        },
        "points": {},
    }
    write_json(state_path, state)
    for name in ("cards.jsonl", "errors.jsonl", "sessions.jsonl"):
        (path / name).touch(exist_ok=True)
    config = path / "course.yaml"
    if not config.exists():
        config.write_text(
            f"course: {args.course}\nmode: {args.mode}\n\nmust_know: []\nkey_points: []\nexam_types: []\nmaterials: {{}}\n",
            encoding="utf-8",
        )
    print(path)


def cmd_record_point(args) -> None:
    path = require_course(args.course, args.root)
    state_path = path / "state.json"
    state = read_json(state_path, {})
    today_s = today()
    points = state.setdefault("points", {})
    current = points.get(args.point, {})
    current.update(
        {
            "level": args.level,
            "status": args.status,
            "source": args.source,
            "updated_at": today_s,
        }
    )
    if args.verification is not None:
        current["verification"] = args.verification
    if args.review_due is not None:
        current["review_due"] = args.review_due
    points[args.point] = current
    state["updated_at"] = today_s
    refresh_point_counts(state)
    write_json(state_path, state)
    print(json.dumps(current, ensure_ascii=False))


def cmd_record_error(args) -> None:
    path = require_course(args.course, args.root)
    item = {
        "date": today(),
        "point": args.point,
        "reason": args.reason,
        "question_type": args.question_type,
        "must_know": args.must_know,
        "status": "stubborn" if args.stubborn else "open",
    }
    errors_path = path / "errors.jsonl"
    append_jsonl(errors_path, item)
    state_path = path / "state.json"
    state = read_json(state_path, {})
    refresh_error_counts(state, list(iter_jsonl(errors_path)))
    state["updated_at"] = today()
    write_json(state_path, state)
    print(json.dumps(item, ensure_ascii=False))


def cmd_resolve_error(args) -> None:
    path = require_course(args.course, args.root)
    errors_path = path / "errors.jsonl"
    errors = list(iter_jsonl(errors_path))
    if not errors:
        fail(f"no error records in {errors_path}")

    if args.index is not None:
        if not 1 <= args.index <= len(errors):
            fail(f"--index {args.index} out of range: errors.jsonl has {len(errors)} record(s)")
        idx = args.index - 1
        record = errors[idx]
        if record.get("status") not in {"open", "stubborn"}:
            fail(
                f"record at index {args.index} is already '{record.get('status')}', "
                "nothing to resolve"
            )
    else:
        idx = None
        for pos in range(len(errors) - 1, -1, -1):
            record = errors[pos]
            if record.get("status") not in {"open", "stubborn"}:
                continue
            if args.point is not None and record.get("point") != args.point:
                continue
            if args.date is not None and record.get("date") != args.date:
                continue
            if args.contains is not None and args.contains not in (record.get("reason") or ""):
                continue
            idx = pos
            break
        if idx is None:
            fail("no matching open/stubborn error record for the given filters; nothing changed")

    record = errors[idx]
    record["status"] = "corrected"
    record["corrected_at"] = today()
    record["repair"] = args.repair
    errors[idx] = record
    write_jsonl(errors_path, errors)

    state_path = path / "state.json"
    state = read_json(state_path, {})
    refresh_error_counts(state, errors)
    state["updated_at"] = today()
    write_json(state_path, state)
    print(json.dumps({"index": idx + 1, **record}, ensure_ascii=False))


def cmd_add_card(args) -> None:
    path = require_course(args.course, args.root)
    item = {
        "date": today(),
        "point": args.point,
        "front": args.front,
        "back": args.back,
        "due": args.due,
        "priority": args.priority,
    }
    cards_path = path / "cards.jsonl"
    append_jsonl(cards_path, item)
    state_path = path / "state.json"
    state = read_json(state_path, {})
    refresh_card_counts(state, list(iter_jsonl(cards_path)))
    state["updated_at"] = today()
    write_json(state_path, state)
    print(json.dumps(item, ensure_ascii=False))


def cmd_log_session(args) -> None:
    path = require_course(args.course, args.root)
    item = {
        "date": today(),
        "action": args.action,
        "topic": args.topic,
        "result": args.result,
    }
    if args.quiz is not None:
        item["quiz"] = args.quiz
    if args.note is not None:
        item["note"] = args.note
    if args.anki is not None:
        item["anki"] = args.anki
    if args.errors_corrected is not None:
        item["errors_corrected"] = args.errors_corrected
    if args.cards_added is not None:
        item["cards_added"] = args.cards_added
    if args.stubborn is not None:
        item["stubborn"] = args.stubborn
    sessions_path = path / "sessions.jsonl"
    if not sessions_path.exists():
        sessions_path.touch()
    append_jsonl(sessions_path, item)
    state_path = path / "state.json"
    state = read_json(state_path, {})
    state["updated_at"] = today()
    write_json(state_path, state)
    print(json.dumps(item, ensure_ascii=False))


def cmd_archive_course(args) -> None:
    source = require_course(args.course, args.root)
    target_root = archive_dir(args.root)
    target = target_root / source.name
    if target.exists():
        fail(f"archive target already exists: {target}; nothing moved")

    state_path = source / "state.json"
    state = read_json(state_path, {})
    state["archived_at"] = today()
    state["archive_reason"] = args.reason
    state["updated_at"] = today()
    write_json(state_path, state)

    target_root.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(target))
    print(f"archived: {target}")


def cmd_restore_course(args) -> None:
    source_root = archive_dir(args.root)
    slug = slugify(args.course)
    source = source_root / slug
    target_root = Path(args.root)
    target = target_root / slug
    if not source.is_dir():
        fail(f"archived course not found: {source}; nothing moved")
    if target.exists():
        fail(f"course already exists: {target}; nothing moved")
    state_path = source / "state.json"
    if not state_path.is_file():
        fail(f"archived course state missing: {state_path}; nothing moved")

    state = read_json(state_path, {})
    state.pop("archived_at", None)
    state.pop("archive_reason", None)
    state["updated_at"] = today()
    write_json(state_path, state)

    target_root.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(target))
    print(f"restored: {target}")


def cmd_status(args) -> None:
    path = require_course(args.course, args.root)
    state = read_json(path / "state.json", {})
    errors = list(iter_jsonl(path / "errors.jsonl"))
    cards = list(iter_jsonl(path / "cards.jsonl"))
    result = {
        "course": state.get("course", args.course),
        "stage": state.get("stage", "unknown"),
        "mode": state.get("mode", "compact"),
        "counts": state.get("counts", {}),
        "open_errors": [item for item in errors if item.get("status") == "open"][-10:],
        "due_cards": [item for item in cards if item.get("due", "") <= dt.date.today().isoformat()][:10],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_summary(args) -> None:
    path = require_course(args.course, args.root)
    state = read_json(path / "state.json", {})
    points = state.get("points", {})
    errors = list(iter_jsonl(path / "errors.jsonl"))
    stubborn = [item for item in errors if item.get("status") == "stubborn"]
    must = {name: data for name, data in points.items() if data.get("level") == "must"}
    print(f"# {state.get('course', args.course)} 复习摘要")
    print()
    print(f"- 阶段: {state.get('stage', 'unknown')}")
    print(f"- 已记录知识点: {len(points)}")
    print(f"- 错题记录: {len(errors)}")
    print(f"- 顽固点: {len(stubborn)}")
    if must:
        print("\n## Must-know 状态")
        for name, data in must.items():
            print(f"- {name}: {data.get('status', 'unknown')}")
    if stubborn:
        print("\n## 顽固点")
        for item in stubborn:
            print(f"- {item.get('point')} ({item.get('reason')})")


def _add_home_options(target: argparse.ArgumentParser) -> None:
    target.add_argument(
        "--data-home",
        type=Path,
        default=argparse.SUPPRESS,
        metavar="DIR",
        help=(
            "data home directory; courses live under DIR/courses "
            "(overrides PASS_ALL_EXAMS_HOME; default: ~/.pass-all-exams); "
            "accepted before or after the subcommand"
        ),
    )
    target.add_argument(
        "--root",
        type=Path,
        default=argparse.SUPPRESS,
        metavar="COURSES_DIR",
        help=(
            "courses directory that directly contains one folder per course; "
            "NOT the data home — passing a data home here would create courses "
            "one level too deep (takes precedence over --data-home); "
            "accepted before or after the subcommand"
        ),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage pass-all-exams course state.")
    _add_home_options(parser)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    _add_home_options(init)
    init.add_argument("--course", required=True)
    init.add_argument("--mode", choices=["compact", "standard", "deep"], default="compact")
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=cmd_init)

    point = sub.add_parser("record-point")
    _add_home_options(point)
    point.add_argument("--course", required=True)
    point.add_argument("--point", required=True)
    point.add_argument("--level", choices=["must", "key", "support"], default="key")
    point.add_argument("--status", choices=["mapped", "taught", "tested", "corrected", "mastered", "stubborn"], default="mapped")
    point.add_argument("--source", choices=["material", "inferred", "needs-confirmation"], default="needs-confirmation")
    point.add_argument("--verification", default=None, help="optional mastery evidence, e.g. the quiz answer or a note")
    point.add_argument("--review-due", type=iso_date, default=None, metavar="YYYY-MM-DD", help="optional retest/review date (ISO)")
    point.set_defaults(func=cmd_record_point)

    error = sub.add_parser("record-error")
    _add_home_options(error)
    error.add_argument("--course", required=True)
    error.add_argument("--point", required=True)
    error.add_argument("--reason", required=True)
    error.add_argument("--question-type", default="unknown")
    error.add_argument("--must-know", action="store_true")
    error.add_argument("--stubborn", action="store_true")
    error.set_defaults(func=cmd_record_error)

    resolve = sub.add_parser("resolve-error")
    _add_home_options(resolve)
    resolve.add_argument("--course", required=True)
    resolve.add_argument("--point", default=None, help="optional filter: exact point name")
    resolve.add_argument("--contains", default=None, help="optional filter: substring match on reason")
    resolve.add_argument("--date", type=iso_date, default=None, metavar="YYYY-MM-DD", help="optional filter: exact record date (ISO)")
    resolve.add_argument("--repair", required=True, help="repair applied (re-explanation angle / retest)")
    resolve.add_argument("--index", type=int, default=None, metavar="N", help="1-based line in errors.jsonl; selects that record directly (other filters ignored)")
    resolve.set_defaults(func=cmd_resolve_error)

    card = sub.add_parser("add-card")
    _add_home_options(card)
    card.add_argument("--course", required=True)
    card.add_argument("--point", required=True)
    card.add_argument("--front", required=True)
    card.add_argument("--back", required=True)
    card.add_argument("--due", default=today())
    card.add_argument("--priority", choices=["low", "normal", "high"], default="normal")
    card.set_defaults(func=cmd_add_card)

    session = sub.add_parser("log-session")
    _add_home_options(session)
    session.add_argument("--course", required=True)
    session.add_argument("--action", required=True, help="e.g. start / resume / drill / retry / summary")
    session.add_argument("--topic", required=True, help="topic or point covered in this session")
    session.add_argument("--result", required=True, help="outcome summary, e.g. pass / fail / partial")
    session.add_argument("--quiz", default=None, help="optional quiz question used")
    session.add_argument("--note", default=None, help="optional note")
    session.add_argument("--anki", default=None, help="optional Anki reference")
    session.add_argument("--errors-corrected", type=int, default=None)
    session.add_argument("--cards-added", type=int, default=None)
    session.add_argument("--stubborn", type=int, default=None)
    session.set_defaults(func=cmd_log_session)

    archive = sub.add_parser("archive-course")
    _add_home_options(archive)
    archive.add_argument("--course", required=True)
    archive.add_argument("--reason", required=True, help="why the course is archived")
    archive.set_defaults(func=cmd_archive_course)

    restore = sub.add_parser("restore-course")
    _add_home_options(restore)
    restore.add_argument("--course", required=True)
    restore.set_defaults(func=cmd_restore_course)

    status = sub.add_parser("status")
    _add_home_options(status)
    status.add_argument("--course", required=True)
    status.set_defaults(func=cmd_status)

    summary = sub.add_parser("summary")
    _add_home_options(summary)
    summary.add_argument("--course", required=True)
    summary.set_defaults(func=cmd_summary)
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.root = resolve_courses_root(args)
    try:
        args.func(args)
    except CommandError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
