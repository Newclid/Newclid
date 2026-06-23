Add a construction
==================

Constructions are defined as ``CatalogEntry`` objects.
The ``ConstructionTool`` base class handles all click routing, snapping, undo, and preview automatically — you only need to describe the slots and provide the final emit function.

See :doc:`../modules/constructions` for a reference overview of the module.

Steps
-----

1. **Create the entry file**

   Add ``src/construction/entries/my_construction.ts``.
   Use an existing entry such as ``midpoint.ts`` as a starting template — it is one of the simpler two-slot constructions.

2. **Define identity fields**

   .. code-block:: typescript

      export const myConstruction: CatalogEntry = {
        name: 'my-construction',
        label: 'My construction',
        shortcut: 'm',           // unique letter, shown in the toolbar tooltip
        icon: '…',               // SVG string or icon key
        slots: […],
        edges: […],
        sketch(slots, scene) { … },
      };

   Choose a ``shortcut`` letter that is not already used by another construction.

3. **Define slots**

   ``slots`` is an ordered array of ``SlotSpec`` — one entry per click the user must make:

   - ``{ kind: 'pick' }`` — the user must click an existing point.
   - ``{ kind: 'free' }`` — the user places a new point anywhere (or snaps to an existing one).
   - ``{ kind: 'derive', fn }`` — the point is computed automatically from already-filled slots; no click required.

4. **Define edges for in-progress feedback**

   ``edges`` is an array of ``[slotIndexA, slotIndexB]`` pairs.
   While the user is filling slots, the renderer draws a line between each pair of already-filled slots so partial progress is visible.

5. **Implement ``sketch``**

   ``sketch(slots, scene)`` is called when all slots are filled.
   It receives the bound points and must emit the final ``GeoObject`` s into the scene:

   .. code-block:: typescript

      sketch(slots, scene) {
        const [a, b] = slots;
        scene.addObject({ kind: 'edge', from: a.id, to: b.id });
      }

6. **Add optional hooks** (if needed)

   - ``validate(slots)`` — return an error string to block the construction (e.g. ``'Points must be distinct'``).
   - ``preview(slots, ctx)`` — draw extra rubber-band geometry while the user hovers.
   - ``onSlotFilled(index, slots)`` — react after each slot is bound (e.g. snap intermediate derived points).

7. **Register in the catalogue**

   Open ``src/construction/catalog.ts`` and import your entry:

   .. code-block:: typescript

      import { myConstruction } from './entries/my_construction';
      // add to the exported array:
      export const catalog: CatalogEntry[] = [
        …,
        myConstruction,
      ];

8. **Add to a toolbar group** (optional)

   Open ``src/tools/groups.ts`` and add the construction ``name`` to the appropriate group array so it appears in the right section of the toolbar.

9. **Verify**

   Run ``npm run dev``, find the tool in the toolbar (or press the shortcut key), and click through each slot.
   Check that the intermediate edges appear and the final object is emitted correctly.
   Press ``Ctrl``/``Cmd``+``Z`` to confirm undo works at each slot boundary.
