import { useEffect } from 'react';
import type { Problem } from '../../api/types';
import { MenuButton } from '../layout/CornerButtons';
import MathDisplay from '../math/MathDisplay';
import './ProblemList.css';

type ProblemListProps = {
  problems: Problem[];
  /** The problem currently being worked on, highlighted in the list */
  currentProblemId: number;
  /** Problems answered correctly at least once, marked with a tick */
  solvedProblemIds: number[];
  /** Called with the index of the clicked problem */
  onSelect: (index: number) => void;
  onClose: () => void;
};

/**
 * The panel that slides in from the left, listing every problem.
 */
export default function ProblemList({
  problems,
  currentProblemId,
  solvedProblemIds,
  onSelect,
  onClose,
}: ProblemListProps) {
  // Close when Escape is pressed
  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') onClose();
    }
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  return (
    <>
      {/* Dims the page behind the panel. Clicking it closes the list. */}
      <div className="problem-list__backdrop" onClick={onClose} />

      <nav className="problem-list" aria-label="Problems">
        <header className="problem-list__header">
          <h2 className="problem-list__title">Problems</h2>
          <span className="problem-list__progress">
            {solvedProblemIds.length} / {problems.length} solved
          </span>
        </header>

        <ol className="problem-list__items">
          {problems.map((problem, index) => {
            const isCurrent = problem.id === currentProblemId;
            const isSolved = solvedProblemIds.includes(problem.id);

            return (
              <li key={problem.id}>
                <button
                  type="button"
                  className={`problem-list__item ${isCurrent ? 'is-current' : ''}`}
                  aria-current={isCurrent ? 'true' : undefined}
                  onClick={() => onSelect(index)}
                >
                  <span className="problem-list__number">{index + 1}</span>
                  <MathDisplay latex={problem.equationLatex} className="problem-list__math" />
                  {isSolved && (
                    <span className="problem-list__solved" aria-label="Solved">
                      ✓
                    </span>
                  )}
                </button>
              </li>
            );
          })}
        </ol>

        {/* The menu button moves onto the panel's edge while the list is open */}
        <MenuButton isOpen onClick={onClose} className="problem-list__toggle" />
      </nav>
    </>
  );
}