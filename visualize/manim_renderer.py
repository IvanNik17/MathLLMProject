import subprocess
import sys
from pathlib import Path

from scene_factory import SceneFactory

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class RenderError(RuntimeError):
    pass


class ManimRenderer:
    """Renders an ExplanationPlan to an mp4. Every render happens in its own folder, so multiple renders can happen at once without interfering with each other."""

    def create_scene_file(self, scene_class, plan, file):

        template = "\n".join([
            f"from visualize.scenes.{scene_class.__module__.split('.')[-1]} import {scene_class.__name__}",
            "from core.explanation_plan import ExplanationPlan",
            "import numpy as np",
            "",
            f"{scene_class.__name__}.PLAN = ExplanationPlan(",
            f"    explanation_type={plan.explanation_type!r},",
            f"    expression={plan.expression!r},",
            f"    correct_points={plan.correct_points!r},",
            f"    student_points={plan.student_points!r},",
            f"    steps={plan.steps!r},",
            f"    wrong_points={plan.wrong_points!r},",
            f"    missing_points={plan.missing_points!r},",
            f"    extra_points={plan.extra_points!r},",
            f"    annotations={plan.annotations!r},",
            f"    explanation_text={plan.explanation_text!r}",
            ")",
            "",
            f"class GeneratedScene({scene_class.__name__}):",
            "    pass",
        ])

        file.write_text(template, encoding="utf-8")
        return file

    def render(self, plan, work_dir=None, timeout=None):
        """Renders the plan and returns the path of the finished mp4."""
        work_dir = Path(work_dir) if work_dir else PROJECT_ROOT / "media" / "test_render"
        work_dir.mkdir(parents=True, exist_ok=True)

        scene_class = SceneFactory.get_scene(plan)
        scene_file = self.create_scene_file(scene_class, plan, work_dir / "generated_scene.py")
        log_file = work_dir / "manim.log"

        command = [
            # sys.executable is the Python running this code, so Manim comes from the same environment as the server
            sys.executable, "-m", "manim", "render",
            "-ql",
            "--media_dir", str(work_dir / "media"),
            "--progress_bar", "none",
            str(scene_file),
            "GeneratedScene",
        ]

        try:
            result = subprocess.run(
                command,
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise RenderError(f"Manim took longer than {timeout} seconds and was stopped") from exc

        log_file.write_text(result.stdout + "\n" + result.stderr, encoding="utf-8")

        if result.returncode != 0:
            last_lines = "\n".join(result.stderr.strip().splitlines()[-15:])
            raise RenderError(
                f"Manim failed with exit code {result.returncode}. Full log: {log_file}\n{last_lines}"
            )

        videos = [
            path for path in (work_dir / "media").rglob("GeneratedScene.mp4")
            if "partial_movie_files" not in path.parts
        ]
        if not videos:
            raise RenderError(f"Manim finished but no video was found. Full log: {log_file}")

        return videos[0]
