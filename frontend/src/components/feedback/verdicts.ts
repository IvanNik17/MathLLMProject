import type { Verdict } from '../../api/types';

export type VerdictTone = 'correct' | 'partial' | 'incorrect';

type VerdictDisplay = {
  title: string;
  subtitle: string;
  tone: VerdictTone;
};

/** The heading text and colour for each verdict the backend can currently send. */
const VERDICT_DISPLAYS: Record<Verdict, VerdictDisplay> = {
  correct: { title: 'Correct', subtitle: 'You found every solution', tone: 'correct' },
  missed_root: { title: 'Partly correct', subtitle: "You're missing a solution", tone: 'partial' },
  extra_root: { title: 'Partly correct', subtitle: "One of your answers isn't a solution", tone: 'partial' },
  wrong_root: { title: 'Not quite', subtitle: "Your answer isn't a solution", tone: 'incorrect' },
  no_real_roots: { title: 'Not quite', subtitle: 'This equation has no real solutions', tone: 'incorrect' },
  correct_no_roots: { title: 'Correct', subtitle: 'This equation has no real solutions', tone: 'correct' },
};

/** Shown instead of missed_root when the student answered "no real solutions" but there are some */
const NO_ANSWER_MISSED: VerdictDisplay = {
  title: 'Not quite',
  subtitle: 'This equation does have real solutions',
  tone: 'incorrect',
};

/** `answeredNoRoots` is true when the student submitted no solutions, i.e. said there are none. */
export function getVerdictDisplay(verdict: string, answeredNoRoots = false): VerdictDisplay {
  // The backend calls this missed_root, but "partly correct" would be wrong when nothing was found
  if (verdict === 'missed_root' && answeredNoRoots) return NO_ANSWER_MISSED;

  return (
    VERDICT_DISPLAYS[verdict as Verdict] ?? { title: 'Checked', subtitle: verdict, tone: 'partial' }
  );
}