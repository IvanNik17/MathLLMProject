import { useRef } from 'react';
import type { MathfieldElement } from 'mathlive';
import AnswerRow from './AnswerRow';
import ShortcutButtons from './ShortcutButtons';
import { createAnswer, type AnswerEntry } from './answerEntry';
import type { MathShortcut } from './shortcuts';
import './AnswerInput.css';

type AnswerInputProps = {
  /** The variable being solved for, typically x */
  variable: string;
  /** The solutions typed so far. The parent page owns this list. */
  answers: AnswerEntry[];
  /** Called with the updated list whenever the student changes anything */
  onAnswersChange: (answers: AnswerEntry[]) => void;
};

export default function AnswerInput({ variable, answers, onAnswersChange }: AnswerInputProps) {
  // A ref to he math field the student used last. Needed because shortcut buttons insert into this one.
  const activeFieldRef = useRef<MathfieldElement | null>(null);
  const cardRef = useRef<HTMLDivElement>(null);

  function updateAnswer(id: number, latex: string) {
    onAnswersChange(answers.map((answer) => (answer.id === id ? { ...answer, latex } : answer)));
  }

  function addSolution() {
    onAnswersChange([...answers, createAnswer()]);
  }

  function removeAnswer(id: number) {
    activeFieldRef.current = null;

    onAnswersChange(answers.filter((answer) => answer.id !== id));
  }

  function clearAll() {
    activeFieldRef.current = null;
    onAnswersChange([createAnswer()]);
  }

  function insertShortcut(shortcut: MathShortcut) {
    let field = activeFieldRef.current;

    // If no field has been used yet (or it was removed), fall back to the first one, or none
    if (!field || !field.isConnected) {
      field = cardRef.current?.querySelector('math-field') ?? null;
    }
    if (!field) return;

    field.insert(shortcut.insert, { focus: true, selectionMode: 'placeholder' });
  }

  return (
    <div className="answer-card" ref={cardRef}>
      <h2 className="answer-card__title">Your answer</h2>

      <div className="answer-card__rows">
        {answers.map((answer) => (
          <AnswerRow
            key={answer.id}
            variable={variable}
            latex={answer.latex}
            onChange={(latex) => updateAnswer(answer.id, latex)}
            onFocus={(field) => (activeFieldRef.current = field)}
            onRemove={() => removeAnswer(answer.id)}
          />
        ))}
      </div>

      <button type="button" className="answer-card__add" onClick={addSolution}>
        + Add a solution
      </button>

      <div className="answer-card__toolbar">
        <ShortcutButtons onInsert={insertShortcut} />
        <button type="button" className="answer-card__clear" onClick={clearAll}>
          Clear
        </button>
      </div>
    </div>
  );
}
