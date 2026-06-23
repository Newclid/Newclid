Frontend scene and geometry
===========================

The scene and geometry layer is the foundation of the canvas.
It holds the in-memory representation of every object the user has drawn and provides all coordinate math — completely free of DOM or rendering concerns so it can be tested in isolation.

Source files: ``src/scene/``, ``src/geometry/``

Scene
-----

``src/scene/scene.ts`` is the single source of truth for the canvas state.

- Stores a flat list of ``GeoObject`` instances (points, circles, constructions).
- Exposes a listener pub-sub: call ``scene.subscribe(fn)`` to react to any mutation.
- Maintains an undo stack capped at 100 snapshots; each snapshot is a full deep copy captured before a user action.
- Key methods: ``addObject()``, ``removeObject()``, ``setTool()``, ``undo()``, ``snapshot()``, ``serialize()``.

Object types are defined in ``src/geometry/types-object.ts``:

- ``PointObject`` — a named point with a ``WorldPoint`` position.
- ``CircleObject`` — a center point and radius.
- ``ConstructionObject`` — a named construction (edge, line, circumcircle, etc.) referencing point ids.

Viewport
--------

``src/geometry/viewport.ts`` models the camera as ``{ center: WorldPoint, scale: number, width: number, height: number }``.

- ``worldToScreen(p)`` / ``screenToWorld(p)`` — convert between coordinate spaces, including the Y-axis flip (world Y increases upward, screen Y increases downward).
- ``pan(dx, dy)`` — shift the camera by screen-pixel deltas.
- ``zoom(factor, screenAnchor)`` — scale while keeping ``screenAnchor`` pinned to the same world point.
- ``fitPoints(points)`` — auto-zoom and center so all provided points are visible.

Coordinate types
----------------

``src/geometry/coords.ts`` defines two branded TypeScript types:

- ``WorldPoint`` — a position in the infinite mathematical plane.
- ``ScreenPoint`` — a pixel position relative to the canvas element.

The factories ``world(x, y)`` and ``screen(x, y)`` create values of the correct type.
The TypeScript compiler rejects any code that passes a ``WorldPoint`` where a ``ScreenPoint`` is expected, catching an entire class of bugs at compile time.

Geometry utilities
------------------

- ``src/geometry/primitives.ts`` — ``distance()``, ``midpoint()``, and other pure math helpers.
- ``src/geometry/hitTest.ts`` — picking logic: given a ``ScreenPoint`` and a scene, returns the nearest ``GeoObject`` within a tolerance (used for point snapping and context menus).
