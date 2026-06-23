Frontend rendering
==================

The rendering layer reads the scene and viewport and produces everything the user sees.
It has no mutable state of its own — a full redraw from the current scene is cheap enough to call on every animation frame.

Source file: ``src/render/renderer.ts``

Two-layer approach
------------------

The canvas is built from two overlapping HTML elements:

- **SVG element** — the static geometry layer: grid, axes, points, edges, circles, and tool previews.
  SVG is used here because individual elements can be styled and picked by the browser with no extra work.
- **Canvas 2D element** — the proof overlay drawn on top of the SVG.
  Canvas is used for the proof sketch because it needs to draw many small decorations (angle arcs, tick marks, parallel marks) that would be unwieldy as SVG elements.

The ``Renderer`` class
----------------------

``Renderer`` is constructed once in ``main.ts`` and holds references to both elements.

- ``draw(scene, viewport, appStore)`` — redraws everything; called whenever the scene, viewport, or active proof step changes.
- ``resize(width, height)`` — updates both elements when the window resizes.

SVG layer
---------

On each ``draw()`` call the SVG content is fully replaced:

- **Grid and axes** — line spacing adapts to the current zoom level so grid lines never become too dense or too sparse.
- **Points** — rendered as small circles; the snap-candidate point is highlighted.
- **Edges and circles** — straight lines and SVG ``<circle>`` elements connecting the scene objects.
- **Tool previews** — rubber-band lines and candidate snap targets drawn while the user is mid-construction.

Canvas layer (proof sketch)
---------------------------

When a proof step is active, the renderer draws a geometry sketch on the Canvas element.
Each step contributes:

- **Premises** — highlighted in amber.
- **Conclusions** — highlighted in green.
- **Equal-angle groups** — color-coded with a rainbow palette.
- **Parallel groups** — matched tick marks on the relevant segments.

Marker types drawn on the Canvas:

- Perpendicular squares at right-angle vertices.
- Angle arcs with optional tick marks for equal angles.
- Tick marks on segments for equal lengths.
- Parallel marks (arrow-like ticks) on parallel segments.

Coordinate transforms
---------------------

All drawing coordinates go through ``Viewport.worldToScreen()`` so the sketch follows the user's current pan and zoom.
The renderer never stores ``ScreenPoint`` values between frames — they are recomputed on every ``draw()`` call.
