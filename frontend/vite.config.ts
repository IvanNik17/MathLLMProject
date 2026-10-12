import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    // MathLive is a large library (~1 MB), which is expected, so don't warn about it.
    chunkSizeWarningLimit: 2000,
  },
});
