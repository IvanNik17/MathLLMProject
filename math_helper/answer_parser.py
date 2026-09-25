import re


class AnswerParser:

    def parse_roots(self, text):

        numbers = re.findall(
            r"-?\d+\.?\d*",
            text
        )

        return [float(number) for number in numbers]
    


if __name__ == '__main__':

    parser = AnswerParser()

    print(parser.parse_roots("The numbers are -2 and 3"))