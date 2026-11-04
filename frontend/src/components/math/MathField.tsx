import { useEffect, useRef } from 'react';
import type { MathfieldElement } from 'mathlive';
import './MathField.css';

type MathFieldProps = {
  /** The current contents, in LaTeX */
  value: string;
  /** Called with the new LaTeX every time the user edits the field */
  onChange: (latex: string) => void;
  /** Called when the field gains focus */
  onFocus?: (field: MathfieldElement) => void;
  /** Put the cursor in this field as soon as it appears */
  autoFocus?: boolean;
  /** Name read out by screen readers */
  ariaLabel?: string;
};

/**
 * Editable math input, built on MathLive's <math-field> element.
 *
 * MathLive does the hard parts (cursor movement, typing "^" to make an exponent, typing "/" to make a fraction, and so on). This component just connects it to React. The parent owns the value, and this reports every change back to it.
 */
export default function MathField({
  value,
  onChange,
  onFocus,
  autoFocus = false,
  ariaLabel = 'Math input',
}: MathFieldProps) {
  // A ref gives us direct access to the <math-field> DOM element.
  const fieldRef = useRef<MathfieldElement>(null);

  // One-time settings, applied when the field first appears.
  useEffect(() => {
    const field = fieldRef.current;
    if (!field) return;

    // disable MathLive's on-screen keyboard and menu
    field.mathVirtualKeyboardPolicy = 'manual';
    field.menuItems = [];

    if (autoFocus) field.focus();
  }, []);

  // Listen for edits and focus. We use addEventListener because these come from the <math-field> element directly, not from React.
  useEffect(() => {
    const field = fieldRef.current;
    if (!field) return;

    const handleInput = () => onChange(field.value);
    const handleFocus = () => onFocus?.(field);

    field.addEventListener('input', handleInput);
    field.addEventListener('focus', handleFocus);

    return () => {
      field.removeEventListener('input', handleInput);
      field.removeEventListener('focus', handleFocus);
    };
  }, [onChange, onFocus]);

  // When the parent changes the value (e.g. the Clear button), copy it into the field
  useEffect(() => {
    const field = fieldRef.current;
    if (field && field.value !== value) {
      field.value = value;
    }
  }, [value]);

  return <math-field ref={fieldRef} className="math-field" aria-label={ariaLabel} />;
}
