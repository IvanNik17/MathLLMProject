import { useEffect, useState } from 'react';
import { fetchProblems, submitAttempt } from './api/api';
import type { AttemptResult, AttemptStatus, Problem } from './api/types';
import AppHeader from './components/layout/AppHeader';
import { GuideButton, MenuButton } from './components/layout/CornerButtons';
import ProgressSteps from './components/layout/ProgressSteps';
import ProblemList from './components/problems/ProblemList';
import StatusMessage from './components/layout/StatusMessage';
import AnswerPage from './pages/AnswerPage';
import CheckingPage from './pages/CheckingPage';
import FeedbackPage from './pages/FeedbackPage';
import './App.css';

/**
 * Where the student is with the current problem. Each phase has its own page.
 */
type Phase = 'answering' | 'checking' | 'feedback';

const STEP_FOR_PHASE: Record<Phase, number> = {
  answering: 1,
  checking: 2,
  feedback: 3,
};

/**
 * The root component. It holds the app's data, talks to the backend (through api.ts), and decides which page to show.
 */
export default function App() {
  // The problems, loaded from the backend
  const [problems, setProblems] = useState<Problem[] | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [problemIndex, setProblemIndex] = useState(0);
  const [solvedProblemIds, setSolvedProblemIds] = useState<number[]>([]);
  const [isProblemListOpen, setIsProblemListOpen] = useState(false);  

  // The current attempt at the current problem
  const [phase, setPhase] = useState<Phase>('answering');
  const [answers, setAnswers] = useState<string[]>([]);
  const [result, setResult] = useState<AttemptResult | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  // The backend's latest report while it checks the attempt (which step it's on)
  const [checkingStatus, setCheckingStatus] = useState<AttemptStatus | null>(null);

  // Load the problems once, when the app starts ([] = no dependencies).
  useEffect(() => {
    let ignore = false;

    fetchProblems()
      .then((loaded) => {
        if (!ignore) setProblems(loaded);
      })
      .catch((error) => {
        if (!ignore) setLoadError(String(error));
      });

    // Cleanup: if the app is removed before the answer arrives, ignore the answer
    return () => {
      ignore = true;
    };
  }, []);

  async function handleSubmit(problem: Problem, submittedAnswers: string[]) {
    setAnswers(submittedAnswers);
    setSubmitError(null);
    setCheckingStatus(null);
    setPhase('checking');

    try {
      const attemptResult = await submitAttempt(problem.id, submittedAnswers, setCheckingStatus);
      setResult(attemptResult);
      setPhase('feedback');
      // Remember correctly solved problems, for the ticks in the problem list.
      if (attemptResult.verdict === 'correct' && !solvedProblemIds.includes(problem.id)) {
        setSolvedProblemIds([...solvedProblemIds, problem.id]);
      }
    } catch (error) {
      const message =
          error instanceof  Error ? error.message: "Soemthing went wrong when checking your asnwer."
      // Go back to the answer page, keeping the answers, and say what went wrong
      setSubmitError(message);
      setPhase('answering');
    }
  }

  function handleTryAgain() {
    // `answers` is kept, so the answer page starts with the previous attempt filled in
    setResult(null);
    setPhase('answering');
  }
  
  /** Switches to the problem at the given position in the list, starting fresh. */
  function selectProblem(index: number) {
    setProblemIndex(index);
    setAnswers([]);
    setResult(null);
    setSubmitError(null);
    setPhase('answering');
    setIsProblemListOpen(false);
  }
  
  function handleNextProblem() {
    if (!problems) return;
    // After the last problem, start again from the first
    selectProblem((problemIndex + 1) % problems.length);
  }


  /** Picks what to show in the middle of the page */
  function renderPage() {
    if (loadError) {
      return (
        <StatusMessage
          title="Couldn't load the problems"
          message={`Is the backend running? (${loadError})`}
          action={{ label: 'Try again', onClick: () => window.location.reload() }}
        />
      );
    }
    if (!problems) {
      return <StatusMessage title="Loading problems..." />;
    }
    if (problems.length === 0) {
      return <StatusMessage title="There are no problems yet" />;
    }

    const problem = problems[problemIndex];

    if (phase === 'checking') {
      return <CheckingPage problem={problem} answers={answers} status={checkingStatus} />;
    }
    if (phase === 'feedback' && result) {
      return (
        <FeedbackPage
          problem={problem}
          answers={answers}
          result={result}
          onTryAgain={handleTryAgain}
          onNextProblem={handleNextProblem}
        />
      );
    }
    return (
      // using a key means a different problem gets a new AnswerPage, so no answers carry over
      <AnswerPage
        key={problem.id}
        problem={problem}
        initialAnswers={answers}
        errorMessage={submitError}
        onSubmit={(submittedAnswers) => handleSubmit(problem, submittedAnswers)}
      />
    );
  }

  const canUseProblemList = phase === 'answering' && problems !== null && problems.length > 0;
  
  return (
    <div className="app">
      <AppHeader />

      {canUseProblemList && (
        <MenuButton isOpen={false} onClick={() => setIsProblemListOpen(true)} />
      )}
      <GuideButton />


      <main className="app__content">{renderPage()}</main>
      
      <ProgressSteps currentStep={STEP_FOR_PHASE[phase]} />

      {canUseProblemList && isProblemListOpen && (
        <ProblemList
          problems={problems}
          currentProblemId={problems[problemIndex].id}
          solvedProblemIds={solvedProblemIds}
          onSelect={selectProblem}
          onClose={() => setIsProblemListOpen(false)}
        />
      )}
    </div>
  );
}
