import { useMemo } from 'react';
import katex from 'katex';
import './MathDisplay.css';

type MathDisplayProps = {
  /** The expression to show, written in LaTeX, e.g. "x^2 - 4 = 0" */
  latex: string;
  /** Optional extra CSS class, e.g. to set the font size */
  className?: string;
};

/** Shows a math expression nicely typeset by using KaTeX to turn LaTeX into html */
export default function MathDisplay({ latex, className = '' }: MathDisplayProps) {
  // Only re-run KaTeX when the LaTeX actually changes.
  const html = useMemo(
    () => katex.renderToString(latex, { throwOnError: false }),
    [latex],
  );

  // dangerouslySetInnerHTML is safe here because the HTML comes from KaTeX
  return (
    <span
      className={`math-display ${className}`}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
