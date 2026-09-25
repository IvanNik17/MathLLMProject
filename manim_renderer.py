import subprocess
from pathlib import Path
import textwrap

from scene_factory import SceneFactory


class ManimRenderer:


    def __init__(self):

        self.output_dir = Path(
            "media/videos"
        )


    def create_scene_file(self, scene_class, plan):

        template = "\n".join([
            f"from scenes.{scene_class.__module__.split('.')[-1]} import {scene_class.__name__}",
            "from explanation_plan import ExplanationPlan",
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

        file = Path("generated_scene.py")
        file.write_text(template,encoding="utf-8")

        return file


    def render(self, plan):

        scene_class = SceneFactory.get_scene(plan)

        generated_file = self.create_scene_file(
            scene_class,
            plan
        )


        print("Generated scene:")
        print(generated_file.read_text())


        command = [
            "python",
            "-m",
            "manim",
            "-ql",
            str(generated_file),
            "GeneratedScene"
        ]


        print("Running:")
        print(" ".join(command))


        result = subprocess.run(
            command,
            text=True
        )


        if result.returncode != 0:
            raise RuntimeError(
                result.stderr
            )

        video_dir = Path(
            "media/videos/generated_scene"
        )

        return video_dir