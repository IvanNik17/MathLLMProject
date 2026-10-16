import re

class AnswerParser:
    def parse_roots(self, text):
        # Extract numerical roots from a student's answer, Supports negative numbers [+-], multiple digits \d+, decimals (?:\.\d*) and so on.

        pattern = r"(?<![\w.])[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?![\w.])"

        numbers = re.findall(pattern, text)

        return [float(number) for number in numbers]


if __name__ == "__main__":
    parser = AnswerParser()

    examples = [
        "The numbers are -2 and 3",
        "The roots are 1.5 and -3.25",
        "Solutions: x = -4, x = 2",
        "The answer is .5 and 2.",
        "Roots: 1e-3 and -2.5e2",
        "No numerical answer here"
        "The answer is zero"
    ]

    for answer in examples:
        print(f"{answer} -> {parser.parse_roots(answer)}")
