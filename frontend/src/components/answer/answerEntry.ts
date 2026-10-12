/**
 * Each entry gets an id so React can tell rows apart when one is removed
 */
export type AnswerEntry = {
  id: number;
  /** What the student typed, in LaTeX */
  latex: string;
};

let nextId = 1;

export function createEmptyAnswer(): AnswerEntry {
  return { id: nextId++, latex: '' };
}
