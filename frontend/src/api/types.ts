export type Problem = {
  id: number;
  title: string;
  /** The equation to show; the backend currently sends SymPy text here. */
  equationLatex: string;
  variable: string;
};

/** The engine's judgement of an attempt. The backend calls this explanation_type. */
export type Verdict = 'correct' | 'missed_root' | 'extra_root' | 'wrong_root' | 'no_real_roots';

export type AttemptResult = {
  problem_id: number;
  answers: string[];
  student_roots: number[];
  verdict: Verdict;
  explanation_text: string;
  video_url: string;
};