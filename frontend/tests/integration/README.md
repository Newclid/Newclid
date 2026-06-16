# Frontend integration tests

Place tests here when several real frontend modules are exercised together.

Examples:

- Construction tool + catalogue entry + scene
- Toolbar + tool registry + application store
- Proof form + JGEX generation + job submission boundary
- Job poller + backend client + application store with HTTP replaced by a test
  double

These tests remain inside the frontend process. Tests involving the actual
backend or Newclid/Yuclid are cross-system end-to-end tests and belong outside
this directory.
