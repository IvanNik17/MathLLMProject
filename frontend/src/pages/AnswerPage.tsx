import { useState } from 'react';
import type { Problem } from '../api/types';
import AppHeader from '../components/layout/AppHeader';
import MathDisplay from '../components/math/MathDisplay';
import AnswerInput from '../components/answer/AnswerInput';
import { createAnswer, type AnswerEntry } from '../components/answer/answerEntry';
import './AnswerPage.css';
import HelpChat from '../components/help/HelpChat';

type AnswerPageProps = {
  problem: Problem;
  initialAnswers: string[];
  errorMessage: string | null;
  onSubmit: (answers: string[]) => void;
};

export default function AnswerPage({ problem, initialAnswers, errorMessage, onSubmit}: AnswerPageProps) {
  const [answers, setAnswers] = useState<AnswerEntry[]>(() =>
    initialAnswers.length > 0 ? initialAnswers.map((latex) => createAnswer(latex)) : [createAnswer()],
  );
const [isHelpOpen, setIsHelpOpen] = useState(false);
  // Only allow checking once no empty boxes are left (e.g. a fraction with nothing below the line).
  // MathLive writes an empty box as "\placeholder{}" in the LaTeX.
  const filledAnswers = answers.map((answer) => answer.latex).filter((latex) => latex.trim() !== '');
  const hasEmptyBoxes = filledAnswers.some((latex) => latex.includes('\\placeholder'));
  // Removing every row means "no real solutions" and sends an empty list.
  // Rows that are all left blank are not the same thing, so they can't be checked.
  const answersNoRoots = answers.length === 0;
  const onlyBlankRows = !answersNoRoots && filledAnswers.length === 0;
  const canCheck = !hasEmptyBoxes && !onlyBlankRows;
  return (
    <div className="answer-page">

      <section id="current-problem">
        <p className="answer-page__instruction" >
          {problem.title} · Solve for {problem.variable}
        </p>
        <MathDisplay latex={problem.equationLatex} className="answer-page__equation" />
      </section>

      <AnswerInput variable={problem.variable} answers={answers} onAnswersChange={setAnswers}/>

      <div className="answer-page__actions">
        {hasEmptyBoxes && <p className="answer-page__hint">Fill in the empty boxes first</p>}
        {onlyBlankRows && (
          <p className="answer-page__hint">
            Type a solution, or remove the row if there are no solutions
          </p>
        )}
        {errorMessage && <p className="answer-page__error">{errorMessage}</p>}

          <button
  type="button"
  className="answer-page__help"
  onClick={() => setIsHelpOpen((open) => !open)}
  aria-expanded={isHelpOpen}
>
  <span>💡</span> Help
</button>
        <button
            id="check-answer"
          type="button"
          className="button button--primary answer-page__check"
          disabled={!canCheck}
          onClick={() => onSubmit(filledAnswers)}
        >
          Check answer
        </button>

      </div>
 {isHelpOpen && (
  <HelpChat
    problem={`${problem.title}: ${problem.equationLatex}`}
    studentAnswer={
      answersNoRoots
        ? 'No real solutions'
        : answers
            .map((answer) => answer.latex)
            .filter(Boolean)
            .join(', ')
    }
    onClose={() => setIsHelpOpen(false)}
  />
)}
    </div>

  );

}
