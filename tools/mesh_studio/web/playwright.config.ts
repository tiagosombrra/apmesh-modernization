import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  // Serialize browser GPU tests to prevent concurrent WebGL load from biasing results.
  workers: 1,
  use: { baseURL: process.env.APMESH_V511_STATIC_BASE_URL ?? 'http://127.0.0.1:5173',
         browserName: 'chromium' },
  // A checked V5.8 launcher can own both servers for the V5.9 reviewer gate.
  webServer: process.env.APMESH_V59_EXTERNAL_SERVERS === '1' ? [] : [
    { command: 'cd ../../.. && python -m uvicorn tools.mesh_studio.web_api:app --host 127.0.0.1 --port 8765',
      url: 'http://127.0.0.1:8765/api/v1/health', timeout: 25000, reuseExistingServer: !process.env.CI },
    { command: 'npm run dev', url: 'http://127.0.0.1:5173', timeout: 25000,
      reuseExistingServer: !process.env.CI },
  ],
});
