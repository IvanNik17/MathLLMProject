import { useEffect, useState } from 'react';
import { fetchProblems, submitAttempt } from './api/api';
import type { AttemptResult, AttemptStatus, CheckedEquation, Problem, ProblemId } from './api/types';
import AppHeader from './components/layout/AppHeader';
import { GuideButton, MenuButton } from './components/layout/CornerButtons';
import ProgressSteps from './components/layout/ProgressSteps';
import ProblemList from './components/problems/ProblemList';
import StatusMessage from './components/layout/StatusMessage';
import AnswerPage from './pages/AnswerPage';
import CheckingPage from './pages/CheckingPage';
import FeedbackPage from './pages/FeedbackPage';
import NewProblemPage from './pages/NewProblemPage';
import { createCustomProblem, loadCustomProblems, saveCustomProblems } from './storage/customProblems';
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
  const [tutorialActive, setTutorialActive] = useState(false);
  const [problems, setProblems] = useState<Problem[] | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  // The problems the student typed in themselves, read from this browser's storage when the app starts
  const [customProblems, setCustomProblems] = useState<Problem[]>(loadCustomProblems);
  // A position in allProblems (see below)
  const [problemIndex, setProblemIndex] = useState(0);
  const [solvedProblemIds, setSolvedProblemIds] = useState<ProblemId[]>([]);
  const [isProblemListOpen, setIsProblemListOpen] = useState(false);
  // True while the "Add your own problem" page is showing
  const [isAddingProblem, setIsAddingProblem] = useState(false);

  // One list for the rest of the app: the backend's problems first, then the student's own
  const allProblems = [...(problems ?? []), ...customProblems];

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
      const attemptResult = await submitAttempt(problem, submittedAnswers, setCheckingStatus);
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
    if (allProblems.length === 0) return;
    // After the last problem, start again from the first
    selectProblem((problemIndex + 1) % allProblems.length);
  }

  /** Stores the changed list of the student's own problems, in the app and in the browser. */
  function updateCustomProblems(changed: Problem[]) {
    setCustomProblems(changed);
    saveCustomProblems(changed);
  }

  function openNewProblemPage() {
    setIsProblemListOpen(false);
    setIsAddingProblem(true);
  }

  /** Called by the new-problem page once the backend has accepted the equation. */
  function handleAddProblem(equation: CheckedEquation) {
    setIsAddingProblem(false);

    // If they already have this exact problem, go to it rather than adding it twice
    const existingIndex = allProblems.findIndex(
      (problem) => problem.isCustom && problem.equationLatex === equation.equationLatex,
    );
    if (existingIndex !== -1) {
      selectProblem(existingIndex);
      return;
    }

    updateCustomProblems([...customProblems, createCustomProblem(equation)]);
    // The new problem goes last in the list, which is the position the list's current length points at
    selectProblem(allProblems.length);
  }

  function handleRemoveProblem(id: ProblemId) {
    const removedIndex = allProblems.findIndex((problem) => problem.id === id);

    updateCustomProblems(customProblems.filter((problem) => problem.id !== id));
    setSolvedProblemIds(solvedProblemIds.filter((solvedId) => solvedId !== id));

    if (removedIndex === problemIndex) {
      // The problem being worked on is gone, so start fresh on the first one. The list stays open.
      setProblemIndex(0);
      setAnswers([]);
      setResult(null);
      setSubmitError(null);
    } else if (removedIndex < problemIndex) {
      // Everything after the removed problem moves up one place, including the current problem
      setProblemIndex(problemIndex - 1);
    }
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
    if (isAddingProblem) {
      return <NewProblemPage onAdd={handleAddProblem} onCancel={() => setIsAddingProblem(false)} />;
    }
    if (allProblems.length === 0) {
      return (
        <StatusMessage
          title="There are no problems yet"
          action={{ label: 'Add your own problem', onClick: openNewProblemPage }}
        />
      );
    }

    const problem = allProblems[problemIndex];

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

  const canUseProblemList =
    phase === 'answering' && !isAddingProblem && problems !== null && allProblems.length > 0;

  return (
    <div className="app" inert={tutorialActive}>
      <AppHeader />

      {canUseProblemList && (
        <MenuButton isOpen={false} onClick={() => setIsProblemListOpen(true)} />
      )}
      {/* The guide points at parts of the answer page, so it is hidden on the new-problem page */}
      {!isAddingProblem && <GuideButton setTutorialActive={setTutorialActive} />}


      <main className="app__content">{renderPage()}</main>
      
      {/* Writing a problem isn't one of the Answer / Check / Feedback steps, so they are hidden then */}
      {!isAddingProblem && <ProgressSteps currentStep={STEP_FOR_PHASE[phase]} />}

      {canUseProblemList && isProblemListOpen && (
        <ProblemList
          problems={allProblems}
          currentProblemId={allProblems[problemIndex].id}
          solvedProblemIds={solvedProblemIds}
          onSelect={selectProblem}
          onAddProblem={openNewProblemPage}
          onRemoveProblem={handleRemoveProblem}
          onClose={() => setIsProblemListOpen(false)}
        />
      )}
    </div>
  );
}
