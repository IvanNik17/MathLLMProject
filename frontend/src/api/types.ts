export type Problem = {
  id: number;
  title: string;
  /** The equation to show, in LaTeX, e.g. "x^{2} - 4 = 0" */
  equationLatex: string;
  variable: string;
};

/** The engine's judgement of an attempt. The backend calls this explanation_type. */
export type Verdict = 'correct' | 'missed_root' | 'extra_root' | 'wrong_root' | 'no_real_roots';

/** The steps the backend works through for each attempt, in order. */
export type AttemptStage = 'checking_math' | 'writing_feedback' | 'animating';

/** What the backend says about an attempt while it works on it (GET /api/attempts/<id>). */
export type AttemptStatus = {
  attempt_id: string;
  problem_id: number;
  /** The step it is on now. 'done' and 'failed' mean it has finished. */
  stage: AttemptStage | 'done' | 'failed';
  stages: AttemptStage[];
  waiting: boolean;
  /** Filled in when stage is 'done' */
  result: AttemptResult | null;
  /** Filled in when stage is 'failed' */
  error: string | null;
};

export type AttemptResult = {
  problem_id: number;
  answers: string[];
  student_roots: number[];
  verdict: Verdict;
  explanation_text: string;
  /** null if the animation couldn't be made (written feedback still arrives) */
  video_url: string | null;
  /** True when a stored animation for a correct answer was reused */
  reused: boolean;
};
