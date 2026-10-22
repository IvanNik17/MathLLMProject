from visualize.scenes.correct_answer_scene import CorrectAnswerScene
from visualize.scenes.missed_solution_scene import MissedSolutionScene
from visualize.scenes.wrong_solution_scene import WrongSolutionScene
from visualize.scenes.extra_solution_scene import ExtraSolutionScene
from visualize.scenes.no_real_solution_scene import NoRealSolutionScene
from visualize.scenes.correct_periodic_answer_scene import CorrectPeriodicAnswerScene 
from visualize.scenes.wrong_periodic_answer_scene import WrongPeriodicAnswerScene
from visualize.scenes.missing_periodic_answer_scene import MissingPeriodicAnswerScene

class SceneFactory:

    @staticmethod
    def get_scene(plan):

        if plan.explanation_type == "wrong_root":

            WrongSolutionScene.PLAN = plan

            return WrongSolutionScene
        
        elif plan.explanation_type == "missed_root":

            MissedSolutionScene.PLAN = plan

            return MissedSolutionScene

        elif plan.explanation_type == "correct":

            CorrectAnswerScene.PLAN = plan

            return CorrectAnswerScene
        
        elif plan.explanation_type == "extra_root":

            ExtraSolutionScene.PLAN = plan

            return ExtraSolutionScene
        
        elif plan.explanation_type == "no_real_roots":

            NoRealSolutionScene.PLAN = plan

            return NoRealSolutionScene
        elif plan.explanation_type == "correct_period":

            CorrectPeriodicAnswerScene.PLAN = plan

            return CorrectPeriodicAnswerScene
        elif plan.explanation_type == "wrong_period":

            WrongPeriodicAnswerScene.PLAN = plan

            return WrongPeriodicAnswerScene
        elif plan.explanation_type == "missing_period":

            MissingPeriodicAnswerScene.PLAN = plan
            return MissingPeriodicAnswerScene

        raise ValueError(
            f"No scene registered for "
            f"{plan.explanation_type}"
        )