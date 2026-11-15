import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  use: { baseURL: 'http://127.0.0.1:5173', browserName: 'chromium' },
  webServer: [
    { command: 'cd ../../.. && python -m uvicorn tools.mesh_studio.web_api:app --host 127.0.0.1 --port 8765',
      url: 'http://127.0.0.1:8765/api/v1/health', timeout: 25000, reuseExistingServer: !process.env.CI },
    { command: 'npm run dev', url: 'http://127.0.0.1:5173', timeout: 25000,
      reuseExistingServer: !process.env.CI },
  ],
});
