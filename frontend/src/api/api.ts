import type { AttemptResult, AttemptStatus, Problem } from './types';

const API_BASE = '/api';

/** How often to ask the backend how an attempt is going, in milliseconds */
const POLL_INTERVAL = 1000;


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

/** Waits the given number of milliseconds */
function wait(milliseconds: number) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}


/** Gets the list of all problems */
export async function fetchProblems(): Promise<Problem[]> {
  return request<Problem[]>('/problems');
}

/** Sends the student's answers for a problem and waits for the backend's verdict. */
export async function submitAttempt(
  problemId: number,
  answers: string[],
  onProgress?: (status: AttemptStatus) => void,
): Promise<AttemptResult> {
  let status = await request<AttemptStatus>('/attempts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      problem_id: problemId,
      answers: answers,
    }),
  });

  while (status.stage !== 'done' && status.stage !== 'failed') {
    onProgress?.(status);
    await wait(POLL_INTERVAL);
    status = await request<AttemptStatus>(`/attempts/${status.attempt_id}`);
  }

  if (status.stage === 'failed' || !status.result) {
    throw new Error(status.error ?? 'Something went wrong when checking your answer.');
  }
  return status.result;
}
