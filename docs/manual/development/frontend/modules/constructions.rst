Frontend constructions
======================

A construction is any multi-step drawing tool the user can invoke from the toolbar — a point, a line, a triangle, a perpendicular, and so on.
The constructions module defines the catalogue of all built-in constructions, the slot-filling framework that drives their click-by-click interaction, and the base class that every construction inherits.

Source files: ``src/construction/catalog.ts``, ``src/construction/catalog-types.ts``, ``src/tools/construction-tool.ts``, ``src/construction/entries/``

CatalogEntry
------------

Each construction is described by a ``CatalogEntry`` (``src/construction/catalog-types.ts``):

- ``name``, ``label``, ``shortcut``, ``icon`` — identity and toolbar display.
- ``slots`` — an ordered array of ``SlotSpec`` values describing what the user must provide at each click:
  pick an existing point, place a free point, derive a point from existing ones, or provide a scalar value.
- ``edges`` / ``circles`` — pairs of slot indices used to draw intermediate geometry while the user is still filling slots.
- ``sketch(slots, scene)`` — called when all slots are filled; emits the final ``GeoObject`` s into the scene.
- ``validate(slots)`` — optional guard that can block the construction from completing (e.g. prevent degenerate cases).
- ``preview(slots, ctx)`` and ``onSlotFilled(index, slots)`` — hooks for live rubber-band feedback and intermediate snapping.

ConstructionTool
----------------

``src/tools/construction-tool.ts`` implements the ``Tool`` interface for all catalogue entries.
It manages the slot-filling lifecycle on each click:

1. Validate the click position against the current slot spec.
2. Find a nearby existing point (within snap tolerance) or create a new free point.
3. Bind the point to the current slot.
4. Emit intermediate edges/circles so the user sees partial progress.
5. When the last slot is filled, call ``CatalogEntry.sketch()`` and reset.

Before each click the tool captures a scene snapshot so Undo (Ctrl+Z) can rewind one slot at a time.
Duplicate detection prevents the same circle or construction from being added twice.

Built-in constructions
----------------------

Around 25 constructions are registered in ``src/construction/catalog.ts``, each implemented as its own file under ``src/construction/entries/``:

- **Basic**: ``point``, ``segment``, ``line``, ``circle``
- **Polygons**: ``triangle``, ``rectangle``, ``parallelogram``
- **Derived points**: ``midpoint``, ``perpendicular`` (foot), ``parallel``, ``foot``, ``angle_bisector``, ``circumcircle``
- **Intersections**: ``intersection_ll`` (line–line), ``intersection_cc`` (circle–circle), ``intersection_lc`` (line–circle)

To add a new construction, see :doc:`../guides/add_a_construction`.
