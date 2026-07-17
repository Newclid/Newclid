Frontend proof UI
=================

The proof UI layer displays the proofs returned by the backend and lets the user navigate them step by step.
It is entirely read-only from the scene's perspective — it only consumes data from ``AppStore`` and never mutates the canvas.

Source files: ``src/ui/proofPanel.ts``, ``src/ui/proofsList.ts``, ``src/ui/proofChoice.ts``, ``src/ui/proofByPointsPanel.ts``

Proof panel
-----------

``proofPanel.ts`` is the main proof display, shown in the left sidebar when a job has results.

- Parses each proof step from the text format ``"N. | premises = (rule) > conclusion"``.
  Premise references such as ``[C0]`` and ``[N1]`` are resolved to their step labels.
- **Sub-step navigation** — the user can step through each premise and conclusion individually.
  The active sub-step drives the proof sketch on the Canvas (see :doc:`rendering`).
- Shows a status banner for the active job: queued, running, proved, failed, timed out.

Proofs list
-----------

``proofsList.ts`` shows a history table for all jobs submitted in the current session.
Each row displays the job name, problem snippet, status, and duration.
Clicking a row makes that job the active one, updating the proof panel and Canvas overlay.

Proof choice
------------

``proofChoice.ts`` is shown when the backend returns more than one proof for the same problem.
It presents a simple selector so the user can pick which proof to display in the panel.

Proof by points panel
---------------------

``proofByPointsPanel.ts`` implements a goal-picking mode:
the user clicks points on the canvas to specify proof goals instead of typing JGEX predicates manually.
When this mode is active, ``AppStore`` holds a goal-pick callback; the canvas click handler invokes it instead of the active construction tool.
