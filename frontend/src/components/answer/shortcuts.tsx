import type { ReactNode } from 'react';
import MathDisplay from '../math/MathDisplay';
import { ExponentIcon, FractionIcon, SquareRootIcon } from './ShortcutIcons';

/** One button in the shortcut row under the answer field. */
export type MathShortcut = {
  /** Unique name, used as its key */
  id: string;
  /** Text for screen readers and the hover tooltip */
  label: string;
  /** What appears on the button */
  icon: ReactNode;
  /**
   * The LaTeX to insert at the cursor. MathLive understands a few special codes:
   *   #@  the thing just before the cursor
   *   #0  whatever is selected, or an empty box if nothing is
   *   #?  an empty box to fill in
   */
  insert: string;
};

/**
 * The shortcut buttons, in the order they appear.
 * To add a button, add an entry here
 */
export const MATH_SHORTCUTS: MathShortcut[] = [
  {
    id: 'exponent',
    label: 'Exponent',
    icon: <ExponentIcon />,
    insert: '#@^{#?}',
  },
  {
    id: 'fraction',
    label: 'Fraction',
    icon: <FractionIcon />,
    insert: '\\frac{#@}{#?}',
  },
  {
    id: 'square-root',
    label: 'Square root',
    icon: <SquareRootIcon />,
    insert: '\\sqrt{#0}',
  },
  {
    id: 'pi',
    label: 'Pi',
    icon: <MathDisplay latex="\pi" className="shortcut-button__math-icon" />,
    insert: '\\pi',
  },
];
