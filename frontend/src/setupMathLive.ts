// One-time setup for MathLive, the library behind the editable math input.
//
// Importing 'mathlive' registers the <math-field> HTML element with the browser,
// so it can be used in JSX like any other tag (see components/math/MathField.tsx).

import { MathfieldElement } from 'mathlive';

// MathLive normally downloads its own copy of the math fonts. KaTeX already has these fonts, so we tell MathLive not to load them again
MathfieldElement.fontsDirectory = null;

// MathLive can play click sounds on key presses. We don't want that(?)
MathfieldElement.soundsDirectory = null;
