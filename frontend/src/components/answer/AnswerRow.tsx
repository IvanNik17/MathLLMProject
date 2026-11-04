import type { MathfieldElement } from 'mathlive';
import MathDisplay from '../math/MathDisplay';
import MathField from '../math/MathField';

type AnswerRowProps = {
  /** The variable being solved for, shown before the "=" */
  variable: string;
  latex: string;
  onChange: (latex: string) => void;
  onFocus: (field: MathfieldElement) => void;
  onRemove: () => void;
};

export default function AnswerRow({ variable, latex, onChange, onFocus, onRemove }: AnswerRowProps) {
  return (
    <div className="answer-row">
      <MathDisplay latex={`${variable} =`} className="answer-row__label" />

      <MathField
        value={latex}
        onChange={onChange}
        onFocus={onFocus}
        autoFocus
        ariaLabel={`Solution for ${variable}`}
      />

      <button
        type="button"
        className="answer-row__remove"
        aria-label="Remove this solution"
        title="Remove this solution"
        onClick={onRemove}
      >
        ×
      </button>
    </div>
  );
}
