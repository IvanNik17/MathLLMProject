import './StatusMessage.css';

type StatusMessageProps = {
  title: string;
  message?: string;
  /** An optional button, e.g. to retry */
  action?: { label: string; onClick: () => void };
};

/** A centred message for whole-page states like "Loading..." */
export default function StatusMessage({ title, message, action }: StatusMessageProps) {
  return (
    <div className="status-message">
      <h1 className="status-message__title">{title}</h1>
      {message && <p className="status-message__text">{message}</p>}
      {action && (
        <button type="button" className="button button--secondary" onClick={action.onClick}>
          {action.label}
        </button>
      )}
    </div>
  );
}