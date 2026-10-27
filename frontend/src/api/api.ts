import type { AttemptResult, Problem } from './types';
import { sympyToLatex } from './sympyToLatex';

const API_BASE = '/api';


async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(API_BASE + path, options);

  if (!response.ok) {
    let message = `The server answered ${response.status} ${response.statusText} for ${path}`;

    try {
      const errorData = await response.json();

      if (typeof errorData.detail === 'object' && errorData.detail !== null) {
        message = errorData.detail.message ?? message;
      } else if (typeof errorData.detail === 'string') {
        message = errorData.detail;
      }
    } catch {
      // Keep the fallback message if the response isn't valid JSON.
    }

    throw new Error(message);
  }

  return (await response.json()) as T;
}


/** Gets the list of all problems */
export async function fetchProblems(): Promise<Problem[]> {
  const problems = await request<Problem[]>('/problems');

  // TEMPORARY: see sympyToLatex.ts, should probably be done on backend instead
  return problems.map((problem) => ({
    ...problem,
    equationLatex: sympyToLatex(problem.equationLatex),
  }));
}

/** Sends the student's answers for a problem and returns the backend's verdict. */
export async function submitAttempt(problemId: number, answers: string[]): Promise<AttemptResult> {
  const result = await request<AttemptResult>('/attempts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      problem_id: problemId,
      answers: answers,
    }),
  });

  return { ...result, video_url: `${result.video_url}?t=${Date.now()}` };
}