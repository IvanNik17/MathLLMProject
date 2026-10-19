import type { Problem } from '../api/types';
import AttemptSummary from '../components/attempt/AttemptSummary';
import './CheckingPage.css';

type CheckingPageProps = {
  problem: Problem;
  answers: string[];
};

/* Shown while the backend works on the attempt. The backend doesn't report its progress, so this is just a spinner. */
export default function CheckingPage({ problem, answers }: CheckingPageProps) {
  return (
    <div className="checking-page">
      <AttemptSummary problem={problem} answers={answers} layout="column" />

      {/* role="status" makes screen readers announce the text inside */}
      <div className="checking-page__card" role="status">
        <h2 className="checking-page__title">Checking your answer</h2>
        <div className="checking-page__spinner" aria-hidden="true" />
        <p className="checking-page__text">
          Checking the math, writing feedback and animating an explanation. This can take a little while.
        </p>
      </div>
    </div>
  );
}