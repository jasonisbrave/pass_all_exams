"""Tests for scripts/examctl.py (stdlib only)."""

from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "examctl.py"
sys.path.insert(0, str(REPO / "scripts"))

import examctl  # noqa: E402


TODAY = dt.date.today().isoformat()


def run(*cli: str, data_home: Path | None = None, root: Path | None = None,
        env_extra: dict | None = None) -> subprocess.CompletedProcess:
    """Run examctl in a subprocess with a clean environment."""
    cmd = [sys.executable, str(SCRIPT)]
    if data_home is not None:
        cmd += ["--data-home", str(data_home)]
    if root is not None:
        cmd += ["--root", str(root)]
    cmd += list(cli)
    env = os.environ.copy()
    env.pop("PASS_ALL_EXAMS_HOME", None)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        cmd, capture_output=True, encoding="utf-8", errors="replace", env=env
    )


def out_json(proc: subprocess.CompletedProcess) -> dict:
    return json.loads(proc.stdout)


class ExamctlTestCase(unittest.TestCase):
    """Base: a temp dir with data/courses + data/archive roots."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base = Path(self._tmp.name)
        self.data = self.base / "data"
        self.courses = self.data / "courses"
        self.archive = self.data / "archive"

    def init(self, course: str = "demo") -> subprocess.CompletedProcess:
        return run("init", "--course", course, root=self.courses)


class TestHomeResolution(ExamctlTestCase):
    def test_env_var_selects_data_home(self) -> None:
        proc = run(
            "init", "--course", "demo",
            env_extra={"PASS_ALL_EXAMS_HOME": str(self.data)},
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((self.courses / "demo" / "state.json").is_file())

    def test_data_home_flag_selects_courses_root(self) -> None:
        proc = run("init", "--course", "demo", data_home=self.data)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((self.courses / "demo" / "state.json").is_file())

    def test_data_home_flag_overrides_env(self) -> None:
        env_home = self.base / "env-home"
        proc = run(
            "init", "--course", "demo",
            data_home=self.data,
            env_extra={"PASS_ALL_EXAMS_HOME": str(env_home)},
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((self.courses / "demo" / "state.json").is_file())
        self.assertFalse((env_home / "courses" / "demo").exists())

    def test_root_flag_takes_precedence_and_points_at_courses(self) -> None:
        explicit = self.base / "plain-courses"
        proc = run("init", "--course", "demo", root=explicit, data_home=self.data)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((explicit / "demo" / "state.json").is_file())
        self.assertFalse(self.courses.exists())

    def test_root_is_courses_dir_not_data_home(self) -> None:
        # Passing a data home to --root must not silently create courses elsewhere;
        # the course lands directly under the given dir (documented behavior).
        proc = run("init", "--course", "demo", root=self.data)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((self.data / "demo" / "state.json").is_file())

    def test_root_help_mentions_courses_dir(self) -> None:
        proc = run("--help")
        self.assertIn("courses directory", proc.stdout)
        self.assertIn("NOT the data home", proc.stdout)

    def test_home_options_accepted_after_subcommand(self) -> None:
        proc = run("init", "--course", "demo", "--data-home", str(self.data))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((self.courses / "demo" / "state.json").is_file())

    def test_root_accepted_after_subcommand_and_wins_over_data_home(self) -> None:
        explicit = self.base / "late-root-courses"
        proc = run("init", "--course", "demo", "--root", str(explicit), data_home=self.data)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((explicit / "demo" / "state.json").is_file())
        self.assertFalse(self.courses.exists())
        proc = run("status", "--course", "demo", "--root", str(explicit), data_home=self.data)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["course"], "demo")

    def test_courses_root_for_pure_functions(self) -> None:
        # Isolate from an ambient PASS_ALL_EXAMS_HOME (the user's machine sets one)
        # without wiping the whole environment (Windows needs it for Path.home()).
        with mock.patch.dict(os.environ):
            os.environ.pop("PASS_ALL_EXAMS_HOME", None)
            self.assertEqual(
                examctl.default_data_home(),
                Path.home() / ".pass-all-exams",
            )
            self.assertEqual(
                examctl.courses_root_for(None),
                Path.home() / ".pass-all-exams" / "courses",
            )
        self.assertEqual(
            examctl.courses_root_for(Path("X") / "dh"),
            Path("X") / "dh" / "courses",
        )
        with mock.patch.dict(os.environ, {"PASS_ALL_EXAMS_HOME": str(self.data)}):
            self.assertEqual(examctl.default_data_home(), self.data)
            self.assertEqual(examctl.courses_root_for(None), self.data / "courses")


class TestNonInitRequiresExistingCourse(ExamctlTestCase):
    NON_INIT_INVOCATIONS = (
        ("status", "--course", "ghost"),
        ("summary", "--course", "ghost"),
        ("record-point", "--course", "ghost", "--point", "P1"),
        ("record-error", "--course", "ghost", "--point", "P1", "--reason", "r"),
        ("add-card", "--course", "ghost", "--point", "P1", "--front", "f", "--back", "b"),
        ("resolve-error", "--course", "ghost", "--repair", "re-explained"),
        ("log-session", "--course", "ghost", "--action", "drill", "--topic", "T", "--result", "pass"),
        ("archive-course", "--course", "ghost", "--reason", "why"),
    )

    def test_missing_course_refused_and_no_dir_created(self) -> None:
        for invocation in self.NON_INIT_INVOCATIONS:
            with self.subTest(command=invocation[0]):
                proc = run(*invocation, root=self.courses)
                self.assertNotEqual(proc.returncode, 0, proc.stdout)
                self.assertIn("course not found", proc.stderr)
                self.assertIn("examctl init", proc.stderr)
                self.assertFalse(
                    (self.courses / "ghost").exists(),
                    "non-init command must not create the course dir",
                )
                if self.courses.exists():
                    self.assertEqual(list(self.courses.iterdir()), [])

    def test_missing_state_json_refused(self) -> None:
        (self.courses / "ghost").mkdir(parents=True)
        proc = run("status", "--course", "ghost", root=self.courses)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("state missing", proc.stderr)
        self.assertIn("examctl init", proc.stderr)

    def test_restore_missing_archive_refused(self) -> None:
        proc = run("restore-course", "--course", "ghost", root=self.courses)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("archived course not found", proc.stderr)
        self.assertFalse(self.archive.exists())


class TestResolveError(ExamctlTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.init()
        run("record-error", "--course", "demo", "--point", "P1", "--reason", "mixing signs", root=self.courses)
        run("record-error", "--course", "demo", "--point", "P2", "--reason", "wrong formula", "--stubborn", root=self.courses)
        run("record-error", "--course", "demo", "--point", "P1", "--reason", "mixing signs again", root=self.courses)

    def read_errors(self) -> list[dict]:
        return [json.loads(line) for line in (self.courses / "demo" / "errors.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]

    def read_state(self) -> dict:
        return json.loads((self.courses / "demo" / "state.json").read_text(encoding="utf-8"))

    def test_resolves_latest_matching_open_record(self) -> None:
        proc = run(
            "resolve-error", "--course", "demo",
            "--point", "P1", "--repair", "re-explained sign rule, retested", root=self.courses,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = out_json(proc)
        self.assertEqual(payload["index"], 3)
        self.assertEqual(payload["status"], "corrected")
        self.assertEqual(payload["corrected_at"], TODAY)
        self.assertEqual(payload["repair"], "re-explained sign rule, retested")
        errors = self.read_errors()
        self.assertEqual([item["status"] for item in errors], ["open", "stubborn", "corrected"])
        state = self.read_state()
        self.assertEqual(state["counts"]["errors"], 3)
        self.assertEqual(state["counts"]["stubborn"], 1)
        self.assertEqual(state["updated_at"], TODAY)

    def test_contains_filter_targets_stubborn_and_updates_counts(self) -> None:
        proc = run(
            "resolve-error", "--course", "demo",
            "--contains", "formula", "--repair", "re-derived formula", root=self.courses,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = out_json(proc)
        self.assertEqual(payload["index"], 2)
        self.assertEqual(payload["status"], "corrected")
        state = self.read_state()
        self.assertEqual(state["counts"]["errors"], 3)
        self.assertEqual(state["counts"]["stubborn"], 0)
        self.assertEqual(state["updated_at"], TODAY)

    def test_index_selects_exact_record(self) -> None:
        proc = run(
            "resolve-error", "--course", "demo",
            "--index", "1", "--repair", "first fixed", root=self.courses,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = out_json(proc)
        self.assertEqual(payload["index"], 1)
        self.assertEqual(self.read_errors()[0]["status"], "corrected")

    def test_no_match_fails_without_changes(self) -> None:
        proc = run(
            "resolve-error", "--course", "demo",
            "--point", "no-such-point", "--repair", "x", root=self.courses,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("no matching open/stubborn", proc.stderr)
        statuses = [item["status"] for item in self.read_errors()]
        self.assertEqual(statuses, ["open", "stubborn", "open"])

    def test_index_out_of_range_fails(self) -> None:
        proc = run("resolve-error", "--course", "demo", "--index", "9", "--repair", "x", root=self.courses)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("out of range", proc.stderr)

    def test_index_on_corrected_record_fails(self) -> None:
        run("resolve-error", "--course", "demo", "--index", "1", "--repair", "x", root=self.courses)
        proc = run("resolve-error", "--course", "demo", "--index", "1", "--repair", "y", root=self.courses)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("already 'corrected'", proc.stderr)

    def test_date_filter_matches_exact_day(self) -> None:
        ok = run("resolve-error", "--course", "demo", "--date", TODAY, "--repair", "x", root=self.courses)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        miss = run("resolve-error", "--course", "demo", "--date", "1999-01-01", "--repair", "y", root=self.courses)
        self.assertNotEqual(miss.returncode, 0)
        self.assertIn("no matching open/stubborn", miss.stderr)


class TestLogSession(ExamctlTestCase):
    def test_appends_record_and_updates_state_date(self) -> None:
        self.init()
        proc = run(
            "log-session", "--course", "demo",
            "--action", "drill", "--topic", "期望理论", "--result", "pass",
            "--quiz", "Why does V(x) matter?", "--note", "retest next week",
            "--anki", "deck::org-behavior", "--errors-corrected", "2",
            "--cards-added", "3", "--stubborn", "1",
            root=self.courses,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        record = out_json(proc)
        self.assertEqual(
            record,
            {
                "date": TODAY,
                "action": "drill",
                "topic": "期望理论",
                "result": "pass",
                "quiz": "Why does V(x) matter?",
                "note": "retest next week",
                "anki": "deck::org-behavior",
                "errors_corrected": 2,
                "cards_added": 3,
                "stubborn": 1,
            },
        )
        sessions = [
            json.loads(line)
            for line in (self.courses / "demo" / "sessions.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(sessions, [record])
        state = json.loads((self.courses / "demo" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["updated_at"], TODAY)
        self.assertEqual(state["points"], {})
        self.assertEqual(state["counts"]["points_done"], 0)

    def test_optional_fields_omitted_when_not_given(self) -> None:
        self.init()
        proc = run(
            "log-session", "--course", "demo",
            "--action", "start", "--topic", "intake", "--result", "ok", root=self.courses,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        record = out_json(proc)
        self.assertEqual(set(record), {"date", "action", "topic", "result"})

    def test_missing_required_arg_fails(self) -> None:
        self.init()
        proc = run("log-session", "--course", "demo", "--action", "drill", "--topic", "T", root=self.courses)
        self.assertNotEqual(proc.returncode, 0)


class TestArchiveRestore(ExamctlTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.init("demo")
        run("record-error", "--course", "demo", "--point", "P1", "--reason", "r1", root=self.courses)

    def read_state(self, path: Path) -> dict:
        return json.loads((path / "state.json").read_text(encoding="utf-8"))

    def test_archive_moves_course_and_stamps_state(self) -> None:
        proc = run("archive-course", "--course", "demo", "--reason", "已考完收官", root=self.courses)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertFalse((self.courses / "demo").exists())
        target = self.archive / "demo"
        self.assertTrue((target / "state.json").is_file())
        self.assertTrue((target / "errors.jsonl").is_file())
        state = self.read_state(target)
        self.assertEqual(state["archived_at"], TODAY)
        self.assertEqual(state["archive_reason"], "已考完收官")
        self.assertEqual(state["updated_at"], TODAY)
        # data intact
        self.assertEqual(state["counts"]["errors"], 1)

    def test_archive_refuses_existing_target_and_keeps_source(self) -> None:
        (self.archive / "demo").mkdir(parents=True)
        proc = run("archive-course", "--course", "demo", "--reason", "x", root=self.courses)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("archive target already exists", proc.stderr)
        self.assertTrue((self.courses / "demo" / "state.json").is_file())

    def test_roundtrip_restores_and_clears_archive_fields(self) -> None:
        run("archive-course", "--course", "demo", "--reason", "season over", root=self.courses)
        proc = run("restore-course", "--course", "demo", root=self.courses)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertFalse((self.archive / "demo").exists())
        state = self.read_state(self.courses / "demo")
        self.assertNotIn("archived_at", state)
        self.assertNotIn("archive_reason", state)
        self.assertEqual(state["updated_at"], TODAY)
        self.assertEqual(state["counts"]["errors"], 1)

    def test_restore_refuses_existing_course_and_keeps_archive(self) -> None:
        run("archive-course", "--course", "demo", "--reason", "x", root=self.courses)
        (self.courses / "demo").mkdir(parents=True)
        proc = run("restore-course", "--course", "demo", root=self.courses)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("course already exists", proc.stderr)
        self.assertTrue((self.archive / "demo" / "state.json").is_file())

    def test_second_archive_and_second_restore_fail(self) -> None:
        run("archive-course", "--course", "demo", "--reason", "x", root=self.courses)
        again = run("archive-course", "--course", "demo", "--reason", "y", root=self.courses)
        self.assertNotEqual(again.returncode, 0)
        self.assertIn("course not found", again.stderr)
        run("restore-course", "--course", "demo", root=self.courses)
        again_restore = run("restore-course", "--course", "demo", root=self.courses)
        self.assertNotEqual(again_restore.returncode, 0)
        self.assertIn("archived course not found", again_restore.stderr)


class TestRecordPointExtras(ExamctlTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.init()

    def read_state(self) -> dict:
        return json.loads((self.courses / "demo" / "state.json").read_text(encoding="utf-8"))

    def test_verification_and_review_due_are_written(self) -> None:
        proc = run(
            "record-point", "--course", "demo", "--point", "期望理论",
            "--level", "must", "--status", "taught",
            "--verification", "retrieval quiz passed: V=I*T example",
            "--review-due", "2026-12-01",
            root=self.courses,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        point = out_json(proc)
        self.assertEqual(point["verification"], "retrieval quiz passed: V=I*T example")
        self.assertEqual(point["review_due"], "2026-12-01")
        state = self.read_state()
        self.assertEqual(state["counts"]["points_done"], 1)

    def test_invalid_review_due_rejected(self) -> None:
        proc = run(
            "record-point", "--course", "demo", "--point", "P1",
            "--review-due", "2026-13-40", root=self.courses,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("ISO date", proc.stderr)

    def test_re_record_preserves_previous_extra_fields(self) -> None:
        run(
            "record-point", "--course", "demo", "--point", "P1",
            "--verification", "evidence-1", "--review-due", "2026-12-01", root=self.courses,
        )
        proc = run("record-point", "--course", "demo", "--point", "P1", "--status", "mastered", root=self.courses)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        state = self.read_state()
        point = state["points"]["P1"]
        self.assertEqual(point["verification"], "evidence-1")
        self.assertEqual(point["review_due"], "2026-12-01")
        self.assertEqual(point["status"], "mastered")
        self.assertEqual(state["counts"]["points_done"], 1)


class TestLegacyFlowRegression(ExamctlTestCase):
    def test_init_record_error_add_card_status_summary(self) -> None:
        init = run("init", "--course", "组织行为学", root=self.courses)
        self.assertEqual(init.returncode, 0, init.stderr)
        course_dir = self.courses / "组织行为学"
        self.assertTrue((course_dir / "state.json").is_file())
        self.assertTrue((course_dir / "cards.jsonl").is_file())
        self.assertTrue((course_dir / "errors.jsonl").is_file())
        self.assertTrue((course_dir / "sessions.jsonl").is_file())
        self.assertTrue((course_dir / "course.yaml").is_file())

        again = run("init", "--course", "组织行为学", root=self.courses)
        self.assertEqual(again.returncode, 0)
        self.assertIn("exists:", again.stdout)

        point = run(
            "record-point", "--course", "组织行为学", "--point", "霍桑实验",
            "--level", "must", "--status", "taught", "--source", "material", root=self.courses,
        )
        self.assertEqual(point.returncode, 0, point.stderr)
        self.assertEqual(out_json(point)["status"], "taught")

        err = run(
            "record-error", "--course", "组织行为学", "--point", "霍桑实验",
            "--reason", "confusion", "--question-type", "选择题",
            "--must-know", "--stubborn", root=self.courses,
        )
        self.assertEqual(err.returncode, 0, err.stderr)
        self.assertEqual(out_json(err)["status"], "stubborn")

        card = run(
            "add-card", "--course", "组织行为学", "--point", "霍桑实验",
            "--front", "霍桑实验说明了什么?", "--back", "关注与生产率相关",
            root=self.courses,
        )
        self.assertEqual(card.returncode, 0, card.stderr)
        self.assertEqual(out_json(card)["priority"], "normal")

        status = run("status", "--course", "组织行为学", root=self.courses)
        self.assertEqual(status.returncode, 0, status.stderr)
        status_data = json.loads(status.stdout)
        self.assertEqual(status_data["course"], "组织行为学")
        self.assertEqual(status_data["counts"]["points_total"], 1)
        self.assertEqual(status_data["counts"]["points_done"], 1)
        self.assertEqual(status_data["counts"]["errors"], 1)
        self.assertEqual(status_data["counts"]["stubborn"], 1)
        self.assertEqual(status_data["counts"]["cards"], 1)
        self.assertEqual(len(status_data["open_errors"]), 0)
        self.assertEqual(len(status_data["due_cards"]), 1)

        summary = run("summary", "--course", "组织行为学", root=self.courses)
        self.assertEqual(summary.returncode, 0, summary.stderr)
        self.assertIn("复习摘要", summary.stdout)
        self.assertIn("Must-know 状态", summary.stdout)
        self.assertIn("顽固点", summary.stdout)
        self.assertIn("霍桑实验", summary.stdout)

    def test_init_force_resets_state(self) -> None:
        self.init("demo")
        run("record-error", "--course", "demo", "--point", "P1", "--reason", "r", root=self.courses)
        forced = run("init", "--course", "demo", "--force", root=self.courses)
        self.assertEqual(forced.returncode, 0, forced.stderr)
        state = json.loads((self.courses / "demo" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["counts"]["errors"], 0)


if __name__ == "__main__":
    unittest.main()
