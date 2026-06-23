import { defineConfig } from 'vitest/config';

const setupFiles = ['tests/setup/testSetup.ts'];

export default defineConfig({
  test: {
    projects: [
      {
        test: {
          name: 'unit',
          include: ['tests/unit/**/*.test.ts'],
          environment: 'jsdom',
          setupFiles,
          environmentOptions: {
            jsdom: {
              url: 'http://localhost:5173',
            },
          },
        },
      },
      {
        test: {
          name: 'integration',
          include: ['tests/integration/**/*.test.ts'],
          environment: 'jsdom',
          setupFiles,
          environmentOptions: {
            jsdom: {
              url: 'http://localhost:5173',
            },
          },
        },
      },
    ],

    coverage: {
      provider: 'v8',
      include: ['src/**/*.ts'],
      exclude: ['src/vite-env.d.ts'],
      reporter: ['text', 'html', 'cobertura'],
      reportsDirectory: 'coverage',
    },
  },
});
