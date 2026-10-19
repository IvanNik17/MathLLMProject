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
};

export function getVerdictDisplay(verdict: string): VerdictDisplay {
  return (
    VERDICT_DISPLAYS[verdict as Verdict] ?? { title: 'Checked', subtitle: verdict, tone: 'partial' }
  );
}