// The problems a student has typed in themselves.

import type { CheckedEquation, Problem } from '../api/types';

const STORAGE_KEY = 'mathwiz.customProblems';

/** Shown above the equation on the answer page, where the backend's problems say "Problem 1" */
const CUSTOM_PROBLEM_TITLE = 'Your problem';

/** Reads the saved problems. Returns an empty list if there are none, or if they can't be read. */
export function loadCustomProblems(): Problem[] {
  try {
    const text = localStorage.getItem(STORAGE_KEY);
    if (!text) return [];

    const saved: unknown = JSON.parse(text);
    if (!Array.isArray(saved)) return [];

    // Keep only entries that have what a problem needs, in case the saved text was damaged or came from an older version
    return saved.filter(isSavedProblem).map((entry) => ({
      id: entry.id,
      title: CUSTOM_PROBLEM_TITLE,
      equationLatex: entry.equationLatex,
      variable: entry.variable,
      isCustom: true,
    }));
  } catch {
    // localStorage can be switched off (some private-browsing modes), and JSON.parse fails on damaged text
    return [];
  }
}

/** Saves the whole list, replacing what was saved before. */
export function saveCustomProblems(problems: Problem[]) {
  const toSave: SavedProblem[] = problems.map((problem) => ({
    id: String(problem.id),
    equationLatex: problem.equationLatex,
    variable: problem.variable,
  }));

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave));
  } catch {
    // If saving isn't possible the problems still work until the page is closed
  }
}

/** Turns an equation the backend has accepted into a problem for the list. */
export function createCustomProblem(equation: CheckedEquation): Problem {
  return {
    // The current time in milliseconds, which is different for every problem a person can add by hand
    id: `custom-${Date.now()}`,
    title: CUSTOM_PROBLEM_TITLE,
    equationLatex: equation.equationLatex,
    variable: equation.variable,
    isCustom: true,
  };
}

/** What one problem looks like in localStorage */
type SavedProblem = {
  id: string;
  equationLatex: string;
  variable: string;
};

function isSavedProblem(entry: unknown): entry is SavedProblem {
  if (typeof entry !== 'object' || entry === null) return false;
  const candidate = entry as Record<string, unknown>;
  return (
    typeof candidate.id === 'string' &&
    typeof candidate.equationLatex === 'string' &&
    typeof candidate.variable === 'string'
  );
}
