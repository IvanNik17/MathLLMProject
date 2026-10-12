import { MATH_SHORTCUTS, type MathShortcut } from './shortcuts';

type ShortcutButtonsProps = {
  /** Called with the chosen shortcut when a button is pressed */
  onInsert: (shortcut: MathShortcut) => void;
};

export default function ShortcutButtons({ onInsert }: ShortcutButtonsProps) {
  return (
    <div className="shortcut-buttons" role="toolbar" aria-label="Math shortcuts">
      {MATH_SHORTCUTS.map((shortcut) => (
        <button
          key={shortcut.id}
          type="button"
          className="shortcut-button"
          title={shortcut.label}
          aria-label={shortcut.label}
          // Stops the button from stealing focus from the math field on click, so the cursor position in the field is kept
          onMouseDown={(event) => event.preventDefault()}
          onClick={() => onInsert(shortcut)}
        >
          {shortcut.icon}
        </button>
      ))}
    </div>
  );
}
