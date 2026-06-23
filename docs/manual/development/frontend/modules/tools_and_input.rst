Frontend tools and input
========================

The input layer translates raw DOM events into tool invocations and viewport changes.
It sits between the browser and the scene — it never reads from the DOM after setup, and it never renders anything.

Source files: ``src/input/``, ``src/tools/``

Tool interface
--------------

Every construction implements the ``Tool`` interface defined in ``src/tools/tool.ts``:

- ``onClick(ctx: ToolContext)`` — called on each canvas left-click.
- ``onMove(ctx: ToolContext)`` — called on mouse move for live previews.
- ``cancel()`` — resets in-progress state (e.g. when the user presses Escape mid-construction).

``ToolContext`` bundles the world position, screen position, current viewport scale, and whether Shift is held.

``getTool(id)`` in ``src/tools/registry.ts`` returns the ``Tool`` instance for a given tool id string.
Tools are singletons — the registry lazily creates each one on first access.

Click dispatch
--------------

``src/input/toolDispatcher.ts`` handles ``mousedown`` on the canvas element:

1. Converts the screen pixel to a ``WorldPoint`` via ``Viewport``.
2. Applies grid snapping (snap is disabled while Shift is held).
3. Builds a ``ToolContext`` and calls ``getTool(scene.tool).onClick(ctx)``.
4. Captures an undo snapshot in the scene before the tool mutates anything.

Right-click on a point opens the point context menu (``src/ui/pointContextMenu.ts``) instead of invoking the active tool.

Pan and zoom
------------

``src/input/panZoom.ts`` handles viewport navigation:

- **Pan** — right-click or middle-click drag; uses pointer capture so panning continues past the canvas edge.
- **Zoom** — Ctrl+wheel or two-finger pinch; zoom is centered on the cursor position so the point under the cursor stays fixed.
- **Trackpad scroll** — plain wheel events (no Ctrl) translate to a pan.

Redraws triggered by pan/zoom are coalesced with ``requestAnimationFrame`` to avoid redundant work.

Keyboard shortcuts
------------------

``src/input/shortcuts.ts`` listens for ``keydown`` on the document:

- ``Ctrl``/``Cmd`` + ``Z`` — undo (rewinds the undo stack in ``Scene``).
- ``Escape`` — cancels the in-progress construction step by step.
- Letter keys — switch the active tool according to each construction's ``shortcut`` field in the catalogue.

Shortcuts are suppressed when the focused element is an ``INPUT`` or ``TEXTAREA``, so typing in the JGEX input or theorem editor is not intercepted.
