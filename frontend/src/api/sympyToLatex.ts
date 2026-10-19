export function sympyToLatex(expression: string): string {
  let latex = expression
    .replace(/\*\*\s*\(([^()]*)\)/g, '^{$1}') // x**(1/2) → x^{1/2}
    .replace(/\*\*\s*([\w.]+)/g, '^{$1}') //      x**2     → x^{2}
    .replace(/\*/g, '') //                         4*x      → 4x
    .replace(/sqrt\(([^()]*)\)/g, '\\sqrt{$1}'); // sqrt(x) → \sqrt{x}

  // The problems are expressions that should equal zero
  if (!latex.includes('=')) {
    latex += ' = 0';
  }
  return latex;
}