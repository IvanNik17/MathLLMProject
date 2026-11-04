import { useState } from 'react';
import type { Problem } from '../api/types';
import AppHeader from '../components/layout/AppHeader';
import MathDisplay from '../components/math/MathDisplay';
import AnswerInput from '../components/answer/AnswerInput';
import { createAnswer, type AnswerEntry } from '../components/answer/answerEntry';
import './AnswerPage.css';

type AnswerPageProps = {
  problem: Problem;
  initialAnswers: string[];
  errorMessage: string | null;
  onSubmit: (answers: string[]) => void;
};

export default function AnswerPage({ problem, initialAnswers, errorMessage, onSubmit }: AnswerPageProps) {
  const [answers, setAnswers] = useState<AnswerEntry[]>(() =>
    initialAnswers.length > 0 ? initialAnswers.map((latex) => createAnswer(latex)) : [createAnswer()],
  );

  // Only allow checking once no empty boxes are left (e.g. a fraction with nothing below the line).
  // MathLive writes an empty box as "\placeholder{}" in the LaTeX.
  const filledAnswers = answers.map((answer) => answer.latex).filter((latex) => latex.trim() !== '');
  const hasEmptyBoxes = filledAnswers.some((latex) => latex.includes('\\placeholder'));
  const canCheck = !hasEmptyBoxes;

  return (
    <div className="answer-page">
      <section>
        <p className="answer-page__instruction">
          {problem.title} · Solve for {problem.variable}
        </p>
        <MathDisplay latex={problem.equationLatex} className="answer-page__equation" />
      </section>

      <AnswerInput variable={problem.variable} answers={answers} onAnswersChange={setAnswers} />

      <div className="answer-page__actions">
        {hasEmptyBoxes && <p className="answer-page__hint">Fill in the empty boxes first</p>}
        {errorMessage && <p className="answer-page__error">{errorMessage}</p>}
        <button
          type="button"
          className="button button--primary answer-page__check"
          disabled={!canCheck}
          onClick={() => onSubmit(filledAnswers)}
        >
          Check answer
        </button>
      </div>

    </div>
  );
}
