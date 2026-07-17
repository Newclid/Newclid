# Newclid Frontend - NOTICE

The Newclid frontend was developed in 2026 as part of the
TU Delft Computer Science and Engineering Software Project, where the project
team worked on extending Newclid with a browser-based interface for editing
geometry problems, submitting solving jobs, and displaying generated proof
information.

## Frontend component authors and contributors

Copyright 2026 Georgi Georgiev, Hristo Bozhkov, Sayf Persevi

This frontend component includes TypeScript source code for the Newclid web
interface, including geometry rendering, problem input, frontend state
management, backend API communication, and proof display UI.

## Third-party software notices

The frontend component uses npm packages for building, developing, testing, and
validating the browser-based Newclid interface. The direct dependencies declared
for the frontend are grouped by purpose below.

### Frontend build and development tooling

* Vite is used as the frontend build tool and development server. It handles
  local development, asset processing, module bundling, and production builds.

* TypeScript is used as the main implementation language and compiler for the
  frontend source code.

* `@types/node` provides TypeScript type definitions for Node.js APIs used by
  frontend tooling, configuration files, and tests.

### Testing and coverage tooling

* Vitest is used for frontend unit tests and component-level tests.

* `@vitest/coverage-v8` is used to generate test coverage reports for the
  Vitest test suite.

* jsdom is used to provide a DOM-like environment during tests, allowing
  browser-oriented frontend code to be tested in a Node.js environment.

* Playwright, through `@playwright/test`, is used for browser-based and
  end-to-end testing of the frontend.

### Integration and development support

* ioredis is declared for frontend-related tooling or integration code that
  needs to communicate with Redis during development or testing.

A generated list of direct and transitive npm package licenses is provided in:

[`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md)

That file is generated from the installed npm dependency tree and should be
regenerated whenever `package.json` or `package-lock.json` changes.

Optional npm dependencies declared by third-party packages but not installed on
the current platform are not included in the generated license index.

