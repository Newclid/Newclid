Frontend state stores
=====================

The store layer holds global state that does not belong to the canvas — job tracking, proof mode, and custom theorem persistence.
Both stores use the same minimal pub-sub pattern as ``Scene``: call ``store.subscribe(fn)`` to receive a callback on every change.

Source files: ``src/store/appStore.ts``, ``src/store/theoremStore.ts``

AppStore
--------

``AppStore`` is the central hub for application-level state:

- **Problem** — the current JGEX problem string (set when the user submits to the prover).
- **Job history** — a ``Map<jobId, JobRecord>`` that accumulates every proof job in the session.
  Each ``JobRecord`` holds the job's status, optional message, and the full result payload once it arrives.
- **Proof mode** — a flag that tells the renderer to show the proof overlay and disables canvas editing.
- **Active proof step** — the step index and sub-step index being highlighted in the proof panel and on the canvas.
- **Panel tab** — tracks whether the left sidebar shows the toolbar or the proof history.
- **Active tool group** — used to show nested tool sub-menus in the toolbar.
- **Goal-pick callback** — a one-shot callback set by the proof-by-points panel when the user needs to pick a goal point on the canvas.

Key methods: ``setProblem()``, ``addJob()``, ``updateJob()``, ``enterProofMode()``, ``exitProofMode()``.

TheoremStore
------------

``TheoremStore`` manages custom theorems defined by the user:

- Theorems are persisted to browser ``localStorage`` so they survive page reloads.
- An in-memory cache avoids repeated ``localStorage`` reads.
- Key methods: ``getAll()``, ``getById(id)``, ``save(theorem)``, ``remove(id)``.

Custom theorems are read from this store and included in every ``submitJob()`` call.
See :doc:`custom_theorems` for how theorems are structured and edited.
