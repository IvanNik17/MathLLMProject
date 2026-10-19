import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const BACKEND_URL = 'http://localhost:8000';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': BACKEND_URL,
      },
  },
  build: {
    // MathLive is a large library (~1 MB), which is expected, so don't warn about it.
    chunkSizeWarningLimit: 2000,
  },
});
