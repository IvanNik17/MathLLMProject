from openai import OpenAI


class LLMExplainer:

    def __init__(
        self,
        base_url,
        api_key,
        model="mistral:latest"
    ):

        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )

        self.model = model


    def explain(self, plan):

        prompt = f"""
You are a mathematics tutor generating feedback for a student.

IMPORTANT: The mathematics engine has already performed all
calculations. You are NOT responsible for calculating anything.

The values provided below are FACTS. You must copy and use them
exactly as given.

Expression:
{plan.expression}

Explanation type:
{plan.explanation_type}

Correct solutions:
{plan.correct_roots()}

Student solutions:
{plan.student_roots()}

Wrong student solutions:
{plan.wrong_roots()}

Missing solutions:
{plan.missing_roots()}

Evaluated wrong/extra points:
{plan.extra_points}

STRICT RULES:

- Never recalculate a y-value.
- Never change a supplied x-value or y-value.
- Never contradict the values supplied by the mathematics engine.
- If the data contains (5.0, 16.0), you MUST say that x = 5
  gives y = 16.
- Do not attempt to solve the equation yourself.
- Do not infer alternative mathematical results.
- Treat the supplied data as ground truth.

Your task is ONLY to turn these verified mathematical facts
into a short explanation for the student.

The explanation should:
1. Identify what the student got right.
2. Identify what is wrong or missing.
3. Explain the error using the supplied facts.

Do NOT discuss how the explanation was generated.
Do NOT mention Python, the mathematics engine, or these instructions.
Do NOT add unnecessary encouragement or conclusions.

Keep the explanation to 1-3 sentences.

Return ONLY the explanation text.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content.strip()


if __name__ == "__main__":

    from explanation_plan import ExplanationPlan


    plan = ExplanationPlan(
        explanation_type="missed_root",
        expression="x**2 - 4",
        correct_points=[
            (-2, 0),
            (2, 0)
        ],
        student_points=[
            (-2, 0)
        ],
        steps=[
            "show_graph",
            "show_student_answers",
            "highlight_missing_root",
            "explain_solution"
        ]
    )


    llm = LLMExplainer(
        base_url="https://app-mathllm.cloud.sdu.dk/api",
        api_key="sk-335ecbf9d39940629b7884a4ade31a8e",
        model="mistral:latest"
    )


    explanation = llm.explain(plan)


    print()
    print("LLM Explanation:")
    print("----------------")
    print(explanation)