import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

// Fonts 
import '@fontsource/dm-sans/400.css';
import '@fontsource/dm-sans/500.css';
import '@fontsource/dm-sans/700.css';
import '@fontsource/dm-sans/800-italic.css';

// KaTeX's stylesheet. Needed for <MathDisplay> and reused by MathLive
import 'katex/dist/katex.min.css';

import './setupMathLive';
import './styles/theme.css';
import './styles/global.css';
import App from './App';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
