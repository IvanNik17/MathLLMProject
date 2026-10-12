import { useState } from 'react';
import AppHeader from '../components/layout/AppHeader';
import { GuideButton, MenuButton } from '../components/layout/CornerButtons';
import ProgressSteps from '../components/layout/ProgressSteps';
import MathDisplay from '../components/math/MathDisplay';
import AnswerInput from '../components/answer/AnswerInput';
import AnswerPreview from '../components/answer/AnswerPreview';
import { createEmptyAnswer, type AnswerEntry } from '../components/answer/answerEntry';
import './AnswerPage.css';

// A hard-coded example problem until problems come from the backend.
const EXAMPLE_PROBLEM = {
  equationLatex: 'x^2 - 4 = 0',
  variable: 'x',
};

export default function AnswerPage() {
  const [answers, setAnswers] = useState<AnswerEntry[]>(() => [createEmptyAnswer()]);

  // Only allow checking once no empty boxes are left (e.g. a fraction with nothing below the line).
  // MathLive writes an empty box as "\placeholder{}" in the LaTeX.
  const hasEmptyBoxes = answers.some((answer) => answer.latex.includes('\\placeholder'));
  const canCheck = !hasEmptyBoxes;

  function handleAnswersChange(newAnswers: AnswerEntry[]) {
    setAnswers(newAnswers);
  }

  return (
    <div className="answer-page">
      <AppHeader />

      <main className="answer-page__content">
        <section className="answer-page__problem">
          <p className="answer-page__instruction">Solve for {EXAMPLE_PROBLEM.variable}</p>
          <MathDisplay latex={EXAMPLE_PROBLEM.equationLatex} className="answer-page__equation" />
        </section>

        <AnswerInput
          variable={EXAMPLE_PROBLEM.variable}
          answers={answers}
          onAnswersChange={handleAnswersChange}
        />

        <div className="answer-page__actions">
          {hasEmptyBoxes && <p className="answer-page__hint">Fill in the empty boxes first</p>}
          <button
            type="button"
            className="check-button"
            disabled={!canCheck}
          >
            Check answer
          </button>
        </div>
      </main>

    </div>
  );
}
