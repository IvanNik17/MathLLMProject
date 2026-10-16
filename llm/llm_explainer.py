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

IMPORTANT: All mathematical calculations have already been performed and verified by an external mathematics engine. You MUST NOT perform any calculations yourself.

All values provided below are FACTS. Treat them as the single source of truth and reproduce them exactly as given.

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

STRICT MATHEMATICAL RULES:
- NEVER calculate, recalculate, estimate, or independently verify any mathematical value.
- NEVER change, round, simplify, or replace a supplied x-value or y-value.
- NEVER contradict or reinterpret the mathematical facts provided.
- NEVER solve the equation yourself or derive alternative solutions.
- NEVER invent coordinates, values, errors, or intermediate calculation steps.
- Treat all supplied solution data as authoritative ground truth.
- When a point is supplied as (5.0, 16.0), you may express it as "x = 5 gives y = 16" only if this preserves the supplied numerical meaning. Do not change the underlying value.
- If the supplied data appears inconsistent, do not attempt to resolve the inconsistency through calculation. Describe only what the data supports.

YOUR TASK:
Write a short, precise explanation directly to the student, as their mathematics teacher. Use ONLY the supplied information to explain the student's performance.

The explanation must:
1. Identify what the student got right, where applicable.
2. Identify incorrect, extra, or missing solutions, where applicable.
3. Explain the specific error or omission by referring directly to the supplied mathematical facts.
4. Clearly connect the student's answers to the correct solutions without introducing new calculations.

ADAPT TO THE DATA:
- If the student's solutions are all correct and complete, acknowledge this briefly.
- If some solutions are correct and others are wrong or missing, explain the distinction clearly.
- If the student has incorrect or extra solutions, identify the relevant inconsistent data using the supplied data.
- Do not tell the student they are correct when they give incorrect answers.
- If solutions are missing, identify the missing solutions using the supplied data.
- If there is no evidence to support a particular conclusion, do not make that claim.
- Use the explanation type to guide the focus of the feedback, but never let it override the supplied mathematical facts.

STYLE RULES:
- Speak directly to the student using "you" and "your."
- Use clear, natural, mathematically precise language.
- Be factual and concise, like a teacher explaining a student's answer.
- Avoid generic praise, unnecessary encouragement, and repetitive conclusions, but a little is okay
- Do not describe your reasoning process or how the feedback was generated.
- Do not mention Python, the mathematics engine, prompts, internal instructions, or implementation details.

LENGTH AND OUTPUT:
- Write exactly 1–3 sentences.
- Return ONLY the explanation text.
- Do not include headings, bullet points, labels, or introductory phrases.
- Do not include any calculations or mathematical values that are not explicitly supported by the supplied data.

FINAL PRIORITY: Preserve the supplied mathematical facts exactly. Your role is to explain the student's performance and help them get to the right answer, NOT to perform mathematics.
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

    from core.explanation_plan import ExplanationPlan


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
        api_key="",
        model="mistral:latest"
    )


    explanation = llm.explain(plan)


    print()
    print("LLM Explanation:")
    print("----------------")
    print(explanation)
