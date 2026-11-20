import { defineConfig } from '@playwright/test';
import base from './playwright.config';

/**
 * Explicit local-desktop qualification, never the hosted CI benchmark.
 * Run only on a physical workstation with --headed and operator attestation.
 */
export default defineConfig({
  ...base,
  testDir: './tests',
  testMatch: 'viewport-r277-desktop.spec.ts',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 240_000,
  use: {
    ...base.use,
    browserName: 'chromium',
    viewport: {width: 1440, height: 900},
    deviceScaleFactor: 1,
    trace: 'off',
    video: 'off',
  },
});
