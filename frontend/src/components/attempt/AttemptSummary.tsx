import type { Problem } from '../../api/types';
import MathDisplay from '../math/MathDisplay';
import './AttemptSummary.css';

type AttemptSummaryProps = {
  problem: Problem;
  answers: string[];
  layout: 'row' | 'column';
};

export default function AttemptSummary({ problem, answers, layout }: AttemptSummaryProps) {
  const answerLatex = `${problem.variable} = ${answers.join(',\\ ')}`;

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