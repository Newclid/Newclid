# Newclid frontend

Web frontend for the Newclid geometry theorem prover.

The frontend is a TypeScript/Vite single-page application. It provides the
browser-based interface for drawing geometry problems, defining goals, submitting
solver jobs to the backend, managing custom theorems, and displaying generated
proof information.

The frontend is intentionally framework-light: UI elements are built directly
with TypeScript and DOM manipulation, while rendering is split between SVG for
interactive construction/editing and Canvas for proof visualization.

## Features

The current frontend supports:

* interactive geometry workspace with pan and zoom;
* construction toolbar for points, lines, circles, triangles, angle bisectors,
  intersections, and other geometry tools;
* visual problem definition from constructed objects;
* direct JGEX problem input for advanced users;
* goal definition through the UI;
* custom theorem creation and local persistence;
* backend job submission and polling;
* proof status display while the backend is solving;
* step-by-step proof display;
* proof highlighting on the canvas;
* redraw flow for regenerated proof sketches;
* frontend unit, integration, and end-to-end tests.

## Requirements

Use Node.js 20+ or 22+. The Docker image uses Node 22.

Install dependencies with:

```sh
npm ci
```

Use `npm install` only when intentionally changing dependencies.

## Running locally

From `frontend/`:

```sh
npm ci
npm run dev
```

The Vite development server runs at:

```text
http://localhost:5173
```

The frontend talks to the backend through the API base configured in the
frontend code/environment. For normal development, run the backend separately or
use the Docker Compose setup from the repository root.

## Building locally

From `frontend/`:

```sh
npm run typecheck
npm run build
```

`npm run build` runs the TypeScript build and creates the production frontend
bundle in `dist/`.

To preview the production build locally, use the Vite preview command if it is
available in `package.json`:

```sh
npm run preview
```

## Running with Docker

The frontend has its own Dockerfile. It builds the Vite app and serves the
static output through nginx.

From the repository root, run only the web container with the development
Compose override:

```sh
docker compose \
  -f docker-compose.yml \
  -f docker-compose.dev.yml \
  up --build web
```

This is useful when you only want to rebuild and inspect the web image.

For the full local stack, run all services:

```sh
docker compose \
  -f docker-compose.yml \
  -f docker-compose.dev.yml \
  up --build
```

The full stack includes the web frontend, backend API, worker, and Redis. The
nginx frontend container proxies `/api/` requests to the backend service.

To stop the stack:

```sh
docker compose \
  -f docker-compose.yml \
  -f docker-compose.dev.yml \
  down
```

## Testing

The frontend uses Vitest for unit and frontend integration tests, and Playwright
for browser/end-to-end tests.

### Unit and frontend integration tests

Run the default frontend test command:

```sh
npm run test
```

Run all Vitest projects:

```sh
npm run test:all
```

Run unit tests in watch mode:

```sh
npm run test:unit
```

Run unit tests once, suitable for CI:

```sh
npm run test:unit:run
```

Run frontend integration tests in watch mode:

```sh
npm run test:integration
```

Run frontend integration tests once, suitable for CI:

```sh
npm run test:integration:run
```

Frontend integration tests exercise multiple real frontend modules together, but
they do not start the real backend, Redis, Newclid, or Yuclid.

### Coverage

Generate frontend test coverage with:

```sh
npm run test:coverage
```

Coverage output is written to `coverage/`.

### End-to-end tests

The frontend uses Playwright for browser-based tests.

Install the Playwright browser if it has not been installed yet:

```sh
npx playwright install chromium
```

Start the frontend first:

```sh
npm run dev
```

Then, in another terminal, run:

```sh
npm run test:e2e
```

The Playwright config uses this frontend URL by default:

```text
http://127.0.0.1:5173
```

To test against another frontend URL, set `FRONTEND_BASE_URL`:

```sh
FRONTEND_BASE_URL=http://127.0.0.1:8080 npm run test:e2e
```

### Frontend-backend end-to-end tests

Frontend-backend e2e tests require both the frontend and backend to be running.

The easiest way is to start the local Docker Compose stack from the repository
root:

```sh
docker compose \
  -f docker-compose.yml \
  -f docker-compose.dev.yml \
  up --build
```

Then run the frontend-backend e2e suite from `frontend/`:

```sh
FRONTEND_BASE_URL=http://127.0.0.1:8080 npm run test:e2e:frontend-backend
```

If you run the frontend locally through Vite instead, use:

```sh
FRONTEND_BASE_URL=http://127.0.0.1:5173 npm run test:e2e:frontend-backend
```

Make sure the backend API, worker, and Redis are also running for this suite.

## Test layout

```text
tests/
├── unit/          # isolated frontend subsystem tests
├── integration/   # multiple real frontend modules working together
├── e2e/           # Playwright browser/end-to-end tests
├── fixtures/      # reusable scenes, jobs, proof results, etc.
├── helpers/       # reusable test builders, fakes, and DOM helpers
└── setup/         # global jsdom setup and browser shims
```

Use `*.test.ts` for test files.

Unit tests should isolate one subsystem and replace external collaborators with
fakes, stubs, or mocks.

Frontend integration tests should use multiple real frontend modules together,
but should not start the real backend or engine.

Cross-system behavior belongs in Playwright e2e tests.

## Project layout

The main source tree is organized by responsibility:

```text
src/
├── api/              backend API client and shared API types
├── construction/     construction catalog and construction metadata
├── geometry/         coordinates, object types, and geometry utilities
├── input/            pointer, keyboard, pan, zoom, and tool dispatch input
├── render/           SVG/canvas rendering logic
├── scene/            frontend scene model and object storage
├── tools/            construction tools and shared tool helpers
├── ui/               toolbar, panels, dialogs, proof UI, app store
├── main.ts           application entry point
├── style.css         global frontend styles
└── vite-env.d.ts     Vite ambient type declarations
```

The design keeps responsibilities separated:

* `geometry/` contains pure geometry and coordinate logic;
* `scene/` stores the current frontend geometry state;
* `tools/` implements user interactions for constructions;
* `render/` draws the current scene and proof state;
* `ui/` owns panels, dialogs, toolbar behavior, and application state;
* `api/` handles communication with the backend.

## Backend communication

The frontend submits geometry problems to the backend as solving jobs. The
backend creates a job, processes it asynchronously, and the frontend polls for
status until the job succeeds or fails.

At a high level, the frontend flow is:

```text
draw or enter problem
define goal
optionally include custom theorems
submit job to backend
poll job status
fetch result
display proof and proof sketch
```

## Custom theorems

The frontend includes a custom theorem manager. Custom theorems are defined as
premises and conclusions, stored locally in the browser, serialized with the
submitted problem, and forwarded to the backend/engine as part of the solving
request.

## Docker notes

The frontend Docker image is a production-style image:

1. build the app with Node;
2. copy `dist/` into nginx;
3. serve static files from nginx;
4. proxy `/api/` to the backend service inside Docker Compose.

For local UI development, prefer `npm run dev`.

For testing the containerized frontend or full local deployment, prefer Docker
Compose.

## Licenses

Frontend third-party npm license information is listed in:

```text
THIRD_PARTY_LICENSES.md
```

Regenerate it after dependency changes:

```sh
npx license-checker-rseidelsohn \
  --markdown \
  --out THIRD_PARTY_LICENSES.md \
  --excludePrivatePackages
```

