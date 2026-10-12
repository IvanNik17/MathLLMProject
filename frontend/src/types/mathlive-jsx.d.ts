// Tells TypeScript that <math-field> is a valid JSX tag.
// <math-field> is a custom element provided by MathLive, not a built-in HTML tag, so without this declaration TypeScript would report an error wherever we use it.

import type { DetailedHTMLProps, HTMLAttributes } from 'react';
import type { MathfieldElement } from 'mathlive';

declare module 'react' {
  namespace JSX {
    interface IntrinsicElements {
      'math-field': DetailedHTMLProps<HTMLAttributes<MathfieldElement>, MathfieldElement>;
    }
  }
}
