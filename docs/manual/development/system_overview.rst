System overview
===============

Newclid solves plane geometry problems: given a construction, its
hypotheses, and one or more goals, it searches for a sequence of deductions
that proves the goals, then writes that sequence out as a human-readable
proof. Yuclid is an optional C++ engine that reimplements Newclid's matching
and deduction machinery natively for speed, exposed back to Python through
the ``py_yuclid`` bindings.

Both engines share the same interface: ``GeometricSolverBuilder`` builds a
solver from a ``RuleMatcher`` and one or more ``Deductor`` objects, and picks
whichever implementation is available. The pure-Python ``PythonDefault``
always works; the Yuclid-backed ``HEDefault`` is used instead when the
optional ``py_yuclid`` package is installed. A caller can override this
choice explicitly with ``with_rule_matcher``/``with_deductors``.

When Yuclid is used, each solver run serializes the problem to Yuclid's
plain-text input format, invokes the ``yuclid`` executable as a subprocess,
and parses its JSON output back into Newclid's deduction types. This adapter
lives in ``yuclid/python/py_yuclid/yuclid_adapter.py``.

The generic rule matcher
-------------------------

Historically, every rule Yuclid could match had its own hand-written C++
matcher: adding a new theorem meant writing and compiling new C++, and a
caller-defined rule had no fast path at all — it could only run through the
pure-Python fallback. The **generic rule matcher** removes that limitation.

It reads a small rule-file syntax (``rule`` / ``require`` / ``conclude`` /
``end``), compiles each rule into a search plan, and runs a
constraint-satisfaction backtracking search over the problem's points to find
concrete matches — all at runtime, with no new C++ required. This is what
lets ``GeometricSolverBuilder.with_additional_rules`` register arbitrary
caller-defined rules and still have the compiled Yuclid engine match them at
native speed, alongside its built-in ones.

See :doc:`yuclid/architecture` for the full pipeline and
:doc:`yuclid/modules/index` for the module-by-module reference.

Who uses this
--------------

Viewclid, a separate project with its own repository, is the generic
matcher's main downstream consumer: it lets end users define custom theorems
at runtime through a web UI, and submits them to Newclid through the
ordinary Python API (``with_additional_rules``), which forwards them to
Yuclid exactly as described above. This repository has no dependency on
Viewclid and does not need to know it exists to be built, tested, or
released — the relationship only goes one way, from Viewclid to Newclid.
