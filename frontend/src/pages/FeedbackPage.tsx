import { useState } from 'react';
import type { AttemptResult, Problem } from '../api/types';
import AttemptSummary from '../components/attempt/AttemptSummary';
import VerdictCard from '../components/feedback/VerdictCard';
import './FeedbackPage.css';

type FeedbackPageProps = {
  problem: Problem;
  answers: string[];
  result: AttemptResult;
  onTryAgain: () => void;
  onNextProblem: () => void;
};

/** The backend's verdict, written feedback and explanation video. */
export default function FeedbackPage({ problem, answers, result, onTryAgain, onNextProblem }: FeedbackPageProps) {
  const [videoFailed, setVideoFailed] = useState(false);

  return (
    <div className="feedback-page">
      <AttemptSummary problem={problem} answers={answers} layout="row" />

      <div className="feedback-page__body">
        <div className="feedback-page__video-frame">
          {videoFailed ? (
            <p className="feedback-page__video-error">The explanation video couldn't be loaded.</p>
          ) : (
            // muted is required for autoPlay in most browsers (the videos have no sound anyway)
            <video
              className="feedback-page__video"
              src={result.video_url}
              controls
              autoPlay
              muted
              playsInline
              onError={() => setVideoFailed(true)}
            />
          )}
        </div>

        <VerdictCard
          verdict={result.verdict}
          explanation={result.explanation_text}
          onTryAgain={onTryAgain}
          onNextProblem={onNextProblem}
        />
      </div>
    </div>
  );
}