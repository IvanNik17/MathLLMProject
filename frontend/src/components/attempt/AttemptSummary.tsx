import type { Problem } from '../../api/types';
import MathDisplay from '../math/MathDisplay';
import './AttemptSummary.css';

type AttemptSummaryProps = {
  problem: Problem;
  answers: string[];
  layout: 'row' | 'column';
};

export default function AttemptSummary({ problem, answers, layout }: AttemptSummaryProps) {
  // No answers means the student said the equation has no real solutions
  const answerLatex =
    answers.length === 0
      ? '\\text{No real solutions}'
      : `${problem.variable} = ${answers.join(',\\ ')}`;

  return (
    <div className={`attempt-summary attempt-summary--${layout}`}>
      <div className="attempt-summary__item">
        <span className="attempt-summary__label">Equation</span>
        <MathDisplay latex={problem.equationLatex} className="attempt-summary__math" />
      </div>
      <div className="attempt-summary__item">
        <span className="attempt-summary__label">Your answer</span>
        <MathDisplay latex={answerLatex} className="attempt-summary__math" />
      </div>
    </div>
  );
}