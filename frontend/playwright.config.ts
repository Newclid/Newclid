import { defineConfig, devices } from '@playwright/test';

const FRONTEND_BASE_URL = process.env.FRONTEND_BASE_URL ?? 'http://127.0.0.1:5173';
const isCI = !!process.env.CI;

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false,
  forbidOnly: isCI,
  retries: isCI ? 1 : 0,
  workers: isCI ? 1 : undefined,
  timeout: 60_000,
  expect: { timeout: 10_000 },
  reporter: isCI
    ? [['line'], ['junit', { outputFile: '../reports/e2e-junit.xml' }]]
    : [['list']],
  use: {
    baseURL: FRONTEND_BASE_URL,
    testIdAttribute: 'data-testid',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
});
