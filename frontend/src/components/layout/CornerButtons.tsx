import './CornerButtons.css';

// The two buttons in the top corners of the page

type MenuButtonProps = {
  isOpen: boolean;
  onClick: () => void;
  /** Extra CSS class, used to place the button differently inside the open problem list */
  className?: string;
};

/** Top-left: opens and closes the problem list. */
export function MenuButton({ isOpen, onClick, className = '' }: MenuButtonProps) {
  return (
    <button
      type="button"
      className={`menu-button ${className}`}
      aria-label={isOpen ? 'Close problem list' : 'Open problem list'}
      aria-expanded={isOpen}
      onClick={onClick}
    >
      <svg width="64" height="64" viewBox="0 0 64 64" aria-hidden="true">
        <g stroke="currentColor" strokeWidth="3" strokeLinecap="round" fill="none">
          <line x1="6" y1="12" x2="52" y2="12" />
          <line x1="6" y1="32" x2="40" y2="32" />
          <line x1="6" y1="52" x2="52" y2="52" />
          {/* The arrow: pointing right (">") to open, left ("<") to close */}
          <polyline
            points={isOpen ? '60,20 50,32 60,44' : '50,20 60,32 50,44'}
            strokeLinejoin="round"
          />
        </g>
      </svg>
    </button>
  );
}

/** Top-right: will open a guide walkthrough. VISUAL ONLY for now. */
export function GuideButton() {
  return (
    <button type="button" className="guide-button" aria-label="Guide">
      <span className="guide-button__box" aria-hidden="true">?</span>
      <span className="guide-button__label">Guide</span>
    </button>
  );
}
