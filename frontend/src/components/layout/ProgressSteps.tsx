import { Fragment } from 'react';
import './ProgressSteps.css';

const STEPS = ['Answer', 'Check', 'Feedback'];

type ProgressStepsProps = {
  /** Which step we're on, counting from 1 */
  currentStep: number;
};

export default function ProgressSteps({ currentStep }: ProgressStepsProps) {
  return (
    <nav className="progress-steps" aria-label="Progress">
      {STEPS.map((name, index) => {
        const stepNumber = index + 1;
        const status =
          stepNumber < currentStep ? 'done' : stepNumber === currentStep ? 'current' : 'upcoming';

        return (
          // Fragment lets us return two elements (a connecting line + a step) without a wrapper.
          <Fragment key={name}>
            {index > 0 && (
              <div className={`progress-steps__line ${stepNumber <= currentStep ? 'is-filled' : ''}`} />
            )}
            <div
              className={`progress-steps__step is-${status}`}
              aria-current={status === 'current' ? 'step' : undefined}
            >
              <span className="progress-steps__circle">{status === 'done' ? '✓' : stepNumber}</span>
              <span className="progress-steps__name">{name}</span>
            </div>
          </Fragment>
        );
      })}
    </nav>
  );
}
