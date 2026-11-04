// Small icons for the shortcut buttons, drawn as SVG. I recommend https://icomoon.io/ if you want to draw new ones

const DASHED = {
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.5,
  strokeDasharray: '3 2.5',
};

export function ExponentIcon() {
  return (
    <svg width="40" height="40" viewBox="0 0 40 40" aria-hidden="true">
      <rect x="4" y="14" width="20" height="22" rx="2" {...DASHED} />
      <rect x="27" y="4" width="10" height="11" rx="1.5" {...DASHED} />
    </svg>
  );
}

export function FractionIcon() {
  return (
    <svg width="40" height="40" viewBox="0 0 40 40" aria-hidden="true">
      <rect x="10" y="2" width="20" height="15" rx="2" {...DASHED} />
      <line x1="6" y1="20" x2="34" y2="20" stroke="currentColor" strokeWidth="1.5" />
      <rect x="10" y="23" width="20" height="15" rx="2" {...DASHED} />
    </svg>
  );
}

export function SquareRootIcon() {
  return (
    <svg width="44" height="40" viewBox="0 0 44 40" aria-hidden="true">
      <polyline
        points="2,24 7,21 13,34 20,6 42,6"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      <rect x="22" y="11" width="18" height="22" rx="2" {...DASHED} />
    </svg>
  );
}
