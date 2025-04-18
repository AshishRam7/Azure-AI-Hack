import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { crx } from '@crxjs/vite-plugin'
import manifest from './manifest.json' assert { type: 'json' };

export default defineConfig({
  plugins: [react(), crx({ manifest })],
  server: {
    port: 3000, // set the port to 3000
  },
});
