Frontend JGEX emission
======================

JGEX is the textual language the Newclid prover reads.
The emission layer converts between the canvas scene and JGEX strings in both directions: the frontend serialises the user's sketch into a JGEX problem, and it parses the JGEX-encoded geometry in the backend's result to drive the proof sketch overlay.

Source files: ``src/emit/jgex.ts``, ``src/emit/jgexParser.ts``, ``src/emit/names.ts``

Emitting JGEX
-------------

``src/emit/jgex.ts`` builds a JGEX problem string from the current scene and any custom theorems.
It iterates over the scene's construction objects, looks up each point's label, and assembles the JGEX clauses for the prover.

Point labels are assigned by ``buildNameTable()`` in ``src/emit/names.ts``, which maps each ``ObjectId`` to a letter ("A", "B", …).
The same table is used for display in the proof panel and for round-tripping through the parser.

Parsing JGEX output
-------------------

``src/emit/jgexParser.ts`` handles the JGEX that comes back from the backend:

- ``parseConstructionSignature(marker)`` — parses a single construction marker string such as ``"eqangle A B C D E F G H"`` into a typed ``ConstructionMarker`` record.
- ``expandJgexPredicates(jgex)`` — expands shorthand predicates into their full forms before further processing.
- ``parseJgexGeometry(jgex)`` — extracts ``SketchGeom`` values (segments, lines, circles, circumcircles) and ``ConstructionMarker`` values (``perp``, ``eqangle``, ``midp``, ``cong``, ``para``, …) from the backend's JGEX output.

The parsed geometry is passed to the renderer to draw the proof sketch overlay on the Canvas element.
