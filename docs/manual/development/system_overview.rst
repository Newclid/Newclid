System overview
===============

Newclid is a solver for plane geometry problems. Given a problem setup made of
points, constructions, hypotheses, and one or more goals, it searches for a
sequence of deductions that proves the goals and can write that sequence out as
a human-readable proof. Yuclid is Newclid's optional C++ engine: a fast,
native implementation of the same deduction/matching machinery, exposed to
Python through the ``py_yuclid`` bindings.

This page gives the big picture. :doc:`repository_layout` describes where the
code for each piece lives, and :doc:`yuclid/index` documents Yuclid's custom
rule matcher in depth.

The high-level pipeline
-----------------------

A Newclid run moves through four stages:

.. code-block:: text

   Problem input (JGEX string, GeoGebra file, or additional rule files)
        │
        ▼
   Parsing into a ProblemSetup (points, constructions, hypotheses, goals)
        │
        ▼
   Deduction / matching (apply rules and algebraic reasoning until the
   goals are proven or no more progress can be made)
        │
        ▼
   Proof output (proof steps, dependency graph, optional diagrams)

- **Input.** Newclid accepts a problem written as a JGEX construction string
  (``newclid jgex ...``) or built from a GeoGebra model (``newclid ggb ...``);
  see :doc:`../building_a_problem_setup/index`. A caller can also register
  additional, non-standard rules at build time (see below), supplied as plain
  Newclid ``Rule`` objects from Python.
- **Parsing.** The JGEX or GeoGebra input is turned into a ``ProblemSetup``:
  concrete points with numeric coordinates, plus the predicates that describe
  the construction's hypotheses and the goals to prove.
- **Deduction/matching.** A ``RuleMatcher`` searches for concrete instances of
  known rules (and, since the custom-rule work, of caller-supplied rules) over
  the problem's points, while one or more ``Deductor`` objects run algebraic
  reasoning (angle chasing, ratio chasing) on top of the matched facts. A
  ``DeductiveAgent`` drives this loop until the goals are proven or the search
  saturates.
- **Output.** Once solved (or saturated), Newclid can write the proof as text
  (see ``newclid/src/newclid/proof_writing.py``), export a dependency graph, or
  render the diagram, depending on what the caller asked for.

Where Yuclid fits
-----------------

The deduction/matching stage is pluggable. Newclid ships a pure-Python
``RuleMatcher``/``Deductor`` implementation (``PythonDefault``) that always
works, and, when the optional ``py_yuclid`` package is installed (``pip install
newclid[yuclid]``), an equivalent implementation backed by the compiled Yuclid
executable (``HEDefault``). ``GeometricSolverBuilder`` picks whichever default
is available unless the caller overrides it explicitly with
``with_rule_matcher``/``with_deductors``.

When Yuclid is used, each solver run is precomputed by serializing the
problem to Yuclid's plain-text input format, invoking the ``yuclid`` binary as
a subprocess, and parsing its JSON output back into Newclid's deduction types.
This adapter layer lives in ``yuclid/python/py_yuclid`` (see
``yuclid_adapter.py``).

Yuclid's **generic rule matcher** is the part of this engine that handles
rules Yuclid does not know about at compile time. Historically, every Yuclid
theorem matcher was hand-written C++ tailored to one specific rule shape, so a
caller-defined rule had no matcher at all unless the Python fallback was used
instead. The generic rule matcher closes that gap: it reads a small rule-file
syntax (``rule`` / ``require`` / ``conclude`` / ``end``) at runtime, compiles
each rule into a search plan, and runs a constraint-satisfaction backtracking
search over the problem's points to find concrete matches — without anyone
having to write new hardcoded C++ for that rule. This is what lets
``GeometricSolverBuilder.with_additional_rules`` register arbitrary
caller-defined rules and still have the compiled Yuclid engine match them, at
native speed, alongside its built-in rules. See :doc:`yuclid/architecture` for
the full pipeline and :doc:`yuclid/modules/index` for the module-by-module
reference.

Downstream consumers
--------------------

Newclid is a library first: the ``newclid`` CLI and the notebooks under
``notebooks/`` are example callers, not the only way to use it. Any Python
program can depend on ``newclid`` (optionally with the ``yuclid`` extra) and
drive it through ``GeometricSolverBuilder``/``GeometricSolver``.

Viewclid, a separate project with its own repository, is one such downstream
consumer: it provides a web frontend and backend that call into Newclid
through the ordinary Python API, including custom rules submitted by its
users. This repository has no dependency on Viewclid, does not import
anything from it, and does not need to know it exists to be built, tested, or
released — the relationship only goes one way, from Viewclid to Newclid.
