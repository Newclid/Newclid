# Frontend tests

The frontend uses Vitest for both unit and frontend integration tests. The two
suites are separate Vitest projects so they can later run as independent GitLab
CI jobs.

## Structure

```text
tests/
├── unit/          # One frontend subsystem isolated from its collaborators
├── integration/   # Multiple real frontend modules working together
├── fixtures/      # Reusable data such as scenes, jobs and proof results
├── helpers/       # Reusable test builders, fakes and DOM helpers
└── setup/         # Global jsdom setup and generic browser shims
```

Cross-system end-to-end tests do not belong here. Tests that start the real
backend or Newclid/Yuclid should live in the repository-level end-to-end suite.

## Naming

Use `*.test.ts` for every test file. Mirror the production subsystem where it
helps navigation, for example:

```text
tests/unit/geometry/viewport.test.ts
tests/unit/scene/scene.test.ts
tests/integration/construction/constructionTool.test.ts
```

## Boundaries

A unit test should instantiate one subsystem and replace external collaborators
with fakes, stubs or mocks.

A frontend integration test should use multiple real frontend modules together,
but it must not start the actual backend, Redis or Newclid/Yuclid.

## Commands

```bash
npm run test
npm run test:all
npm run test:unit
npm run test:unit:run
npm run test:integration
npm run test:integration:run
npm run test:coverage
```

The non-`run` commands use watch mode. The `run` commands execute once and are
intended for CI.

## Rules

- Import `describe`, `it`, `expect` and `vi` explicitly from `vitest`.
- Test observable behaviour instead of private implementation details.
- Do not depend on test execution order.
- Reset timers, DOM state and browser storage between tests.
- Put reusable data in `fixtures/`, not directly in setup files.
- Put only generic browser shims in `setup/`.
