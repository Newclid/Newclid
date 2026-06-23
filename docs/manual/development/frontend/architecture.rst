Frontend architecture
=====================

The frontend is written in vanilla TypeScript with no UI framework.
Vite handles bundling and the dev server.
The code is organised into discrete layers — each with a single responsibility — that communicate through well-defined interfaces rather than shared globals.

Layers
------

.. code-block:: text

   ┌─────────────────────────────────────────┐
   │  UI layer       (src/ui/)               │  dialogs, panels, toolbar
   ├─────────────────────────────────────────┤
   │  Store layer    (src/store/)            │  global pub-sub state
   ├─────────────────────────────────────────┤
   │  Render layer   (src/render/)           │  SVG scene + Canvas proof overlay
   ├─────────────────────────────────────────┤
   │  Input layer    (src/input/)            │  click, pan/zoom, keyboard
   ├─────────────────────────────────────────┤
   │  Scene layer    (src/scene/)            │  in-memory object store + undo
   ├─────────────────────────────────────────┤
   │  Geometry layer (src/geometry/)         │  pure coordinate math, no DOM
   └─────────────────────────────────────────┘

**Geometry layer** — pure functions for coordinate transforms, distance, hit-testing, and viewport math.
Has no side effects and no DOM dependency, so it can be tested in isolation.

**Scene layer** — the single source of truth for what objects exist on the canvas.
Exposes a listener pattern so any layer can react to mutations.
Maintains an undo stack (capped at 100 snapshots).

**Input layer** — translates raw DOM events (clicks, wheel, keyboard) into intent.
Clicks are routed to the active tool; pan/zoom gestures update the viewport; keyboard shortcuts switch tools or trigger undo.

**Render layer** — reads the scene and viewport to produce a visual.
Uses SVG for the static geometry (grid, axes, objects) and a Canvas 2D overlay for proof-step sketches.

**Store layer** — holds state that does not belong to the canvas: the current JGEX problem string, backend job history, proof mode flag, and custom theorems.
Uses the same listener pattern as the scene.

**UI layer** — builds and updates DOM panels (toolbar, proof panel, theorem manager).
Reads from stores and the scene; never writes to the geometry or scene directly.

Entry point
-----------

``src/main.ts`` is the wiring file.
It creates the scene, viewport, renderer, stores, and UI components, then attaches event listeners.
It also owns the job lifecycle: calling the backend client, starting the poller, and entering proof mode when results arrive.

Tool framework
--------------

Every construction (point, line, triangle, …) implements the ``Tool`` interface (``src/tools/tool.ts``).
``getTool()`` in ``src/tools/registry.ts`` returns the right instance for a given tool id.
``ConstructionTool`` (``src/tools/construction-tool.ts``) is the base class used by all constructions; it manages slot filling, snapping, preview rendering, and undo capture.

The construction *catalogue* (``src/construction/catalog.ts``) is a registry of ``CatalogEntry`` objects — one per construction — that describe slots, edges, keyboard shortcut, and the final emit function.
Adding a new construction means adding an entry here; see :doc:`guides/add_a_construction`.

Coordinate safety
-----------------

The codebase uses branded TypeScript types — ``WorldPoint`` and ``ScreenPoint`` — to prevent accidentally mixing canvas coordinates and screen pixel coordinates at compile time.
All geometry math operates on ``WorldPoint``; the renderer converts to ``ScreenPoint`` through ``Viewport``.

Data flow
---------

A typical user interaction follows this path:

1. User clicks the canvas.
2. ``toolDispatcher`` converts the screen pixel to a ``WorldPoint``, snaps to grid, and calls the active tool.
3. The tool mutates the scene (adds or modifies ``GeoObject`` s).
4. The scene notifies listeners; the renderer redraws.
5. When the user submits a proof, ``main.ts`` serialises the scene to JGEX and calls ``BackendClient.submitJob()``.
6. ``JobPoller`` polls the backend every 2 seconds and updates ``AppStore`` with status and results.
7. ``AppStore`` notifies listeners; the proof panel and renderer update to show the proof.
