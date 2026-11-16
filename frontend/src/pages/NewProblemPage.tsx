import { useRef, useState } from 'react';
import type { MathfieldElement } from 'mathlive';
import { checkCustomProblem } from '../api/api';
import type { CheckedEquation } from '../api/types';
import ShortcutButtons from '../components/answer/ShortcutButtons';
import type { MathShortcut } from '../components/answer/shortcuts';
import MathDisplay from '../components/math/MathDisplay';
import MathField from '../components/math/MathField';
import './NewProblemPage.css';

type NewProblemPageProps = {
  /** Called with the equation once the backend has accepted it */
  onAdd: (equation: CheckedEquation) => void;
  onCancel: () => void;
};

/**
 * Where a student types in a problem of their own.
 *
 * It reuses the math field and shortcut buttons from the answer page, but is styled in its own colour (see NewProblemPage.css) so it is clear this is the problem being written, not an answer.
 */
export default function NewProblemPage({ onAdd, onCancel }: NewProblemPageProps) {
  const [latex, setLatex] = useState('');
  const [isChecking, setIsChecking] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // The math field, so the shortcut buttons can insert into it
  const fieldRef = useRef<MathfieldElement | null>(null);

  const isEmpty = latex.trim() === '';
  const hasEmptyBoxes = latex.includes('\\placeholder');
  const canAdd = !isEmpty && !hasEmptyBoxes && !isChecking;

  function handleChange(newLatex: string) {
    setLatex(newLatex);
    // The old message was about what was typed before
    setErrorMessage(null);
  }

  function handleClear() {
    handleChange('');
    // Put the cursor back in the field, ready for typing
    fieldRef.current?.focus();
  }

  function insertShortcut(shortcut: MathShortcut) {
    fieldRef.current?.insert(shortcut.insert, { focus: true, selectionMode: 'placeholder' });
  }

  async function handleAdd() {
    setIsChecking(true);
    setErrorMessage(null);

    try {
      // The backend decides whether this is an equation it can solve and draw
      const equation = await checkCustomProblem(latex);
      onAdd(equation);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Something went wrong when checking the equation.');
      setIsChecking(false);
    }
  }

  return (
    <div className="new-problem-page">
      <header>
        <p className="new-problem-page__tag">New problem</p>
        <h1 className="new-problem-page__title">Add your own problem</h1>
        <p className="new-problem-page__intro">
          Type the equation you want to solve, using x. You write your answer afterwards.
        </p>
      </header>

      <div className="new-problem-card">
        <h2 className="new-problem-card__title">The equation</h2>

        <div className="new-problem-card__field">
          <MathField
            value={latex}
            onChange={handleChange}
            onFocus={(field) => (fieldRef.current = field)}
            autoFocus
            ariaLabel="The equation of your problem"
          />
        </div>

        <div className="new-problem-card__toolbar">
          <ShortcutButtons onInsert={insertShortcut} />
          <button type="button" className="new-problem-card__clear" onClick={handleClear}>
            Clear
          </button>
        </div>

        <p className="new-problem-card__hint">
          For example <MathDisplay latex="x^2 - 5x + 6 = 0" />. Equations whose solutions repeat
          forever, like <MathDisplay latex="\sin(x) = 0" />, can't be used yet.
        </p>
      </div>

      {errorMessage && (
        <p className="new-problem-page__error" role="alert">
          This can't be used as a problem: {errorMessage}
        </p>
      )}

      <div className="new-problem-page__actions">
        <p className="new-problem-page__note">
          Your problems are saved in this browser only. Nobody else can see them, and they disappear if you clear your browser data.
        </p>
        <button type="button" className="button button--secondary" onClick={onCancel}>
          Cancel
        </button>
        <button
          type="button"
          className="button new-problem-page__add"
          disabled={!canAdd}
          onClick={handleAdd}
        >
          {isChecking ? 'Checking...' : 'Add problem'}
        </button>
      </div>
    </div>
  );
}
