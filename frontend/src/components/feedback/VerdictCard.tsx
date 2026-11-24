import { getVerdictDisplay } from './verdicts';
import './VerdictCard.css';

type VerdictCardProps = {
  verdict: string;
  /** True when the student submitted no solutions, i.e. answered "no real solutions" */
  answeredNoRoots: boolean;
  explanation: string;
  onTryAgain: () => void;
  onNextProblem: () => void;
};

const TONE_ICONS = { correct: '✓', partial: '–', incorrect: '✕' };

/** The card beside the video; verdict, written feedback, retry/next buttons */
export default function VerdictCard({ verdict, answeredNoRoots, explanation, onTryAgain, onNextProblem }: VerdictCardProps) {
  const display = getVerdictDisplay(verdict, answeredNoRoots);

  return (
    <section className={`verdict-card verdict-card--${display.tone}`}>
      <header className="verdict-card__header">
        <span className="verdict-card__icon" aria-hidden="true">
          {TONE_ICONS[display.tone]}
        </span>
        <div>
          <h2 className="verdict-card__title">{display.title}</h2>
          <p className="verdict-card__subtitle">{display.subtitle}</p>
        </div>
      </header>

      <div className="verdict-card__feedback">
        <h3 className="verdict-card__label">Feedback</h3>
        <p className="verdict-card__explanation">{explanation}</p>
      </div>

      <div className="verdict-card__actions">
        <button type="button" className="button button--secondary" onClick={onTryAgain}>
          Try again
        </button>
        <button type="button" className="button button--primary" onClick={onNextProblem}>
          Next problem
        </button>
      </div>
    </section>
  );
}