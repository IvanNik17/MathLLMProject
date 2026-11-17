
import { sendHelpMessage } from '../../api/api';
import './HelpChat.css';
import { useEffect, useRef, useState } from 'react';

type HelpChatProps = {
  problem: string;
  studentAnswer: string;
  onClose: () => void;
};

export default function HelpChat({
  problem,
  studentAnswer,
  onClose,
}: HelpChatProps) {
  const [hint, setHint] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const initialHintRequested = useRef(false);
  async function handleGetHint() {
    if (loading) return;

    setLoading(true);
    setError(null);

    try {
      const result = await sendHelpMessage(problem, studentAnswer);
      setHint(result.response);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Could not generate a hint.',
      );
    } finally {
      setLoading(false);
    }
  }
useEffect(() => {
  if (initialHintRequested.current) return;

  initialHintRequested.current = true;
  void handleGetHint();
}, []);
  return (
    <section className="help-chat">
      <button
        type="button"
        onClick={onClose}
        className="help-chat__close"
        aria-label="Close help"
      >
        ×
      </button>

      <button
        type="button"
        className="help-chat__send"
        onClick={() => void handleGetHint()}
        disabled={loading}
      >
        {loading
          ? 'Generating hint...'
          : hint
            ? 'Get another hint'
            : 'Give me a hint'}
      </button>

      {error && (
        <p className="help-chat__error">{error}</p>
      )}

      {hint && (
        <div className="help-chat__message" aria-live="polite">
          {hint}
        </div>
      )}
    </section>
  );
}
