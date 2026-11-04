import type { AttemptStage, AttemptStatus, Problem } from '../api/types';
import AttemptSummary from '../components/attempt/AttemptSummary';
import './CheckingPage.css';

type CheckingPageProps = {
  problem: Problem;
  answers: string[];
  /** The backend's latest report on the attempt, or null before the first one arrives */
  status: AttemptStatus | null;
};

/** What each backend step is called on the page */
const STAGE_NAMES: Record<AttemptStage, string> = {
  checking_math: 'Checking the math',
  writing_feedback: 'Writing feedback',
  animating: 'Animating an explanation',
};

const STAGE_ORDER: AttemptStage[] = ['checking_math', 'writing_feedback', 'animating'];

/* Shown while the backend works on the attempt */
export default function CheckingPage({ problem, answers, status }: CheckingPageProps) {
  // Before the first report, treat it as being on the first step
  const currentStage = status?.stage ?? 'checking_math';
  const currentIndex = STAGE_ORDER.indexOf(currentStage as AttemptStage);

  return (
    <div className="checking-page">
      <AttemptSummary problem={problem} answers={answers} layout="column" />

      {/* role="status" makes screen readers announce the text inside */}
      <div className="checking-page__card" role="status">
        <h2 className="checking-page__title">Checking your answer</h2>

        <ol className="checking-page__stages">
          {STAGE_ORDER.map((stage, index) => {
            const state = index < currentIndex ? 'done' : index === currentIndex ? 'current' : 'upcoming';

            return (
              <li key={stage} className={`checking-page__stage is-${state}`}>
                <span className="checking-page__marker" aria-hidden="true">
                  {state === 'done' && '✓'}
                  {state === 'current' && <span className="checking-page__spinner" />}
                </span>
                {STAGE_NAMES[stage]}
              </li>
            );
          })}
        </ol>

        <p className="checking-page__text">
          {status?.waiting
            ? 'Lots of students are working right now, so this step is waiting for its turn.'
            : 'This can take a little while.'}
        </p>
      </div>
    </div>
  );
}
