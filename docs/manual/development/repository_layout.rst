Repository layout
=================

This repository is a `uv <https://docs.astral.sh/uv/>`_ workspace with three
Python packages plus a documentation tree. The workspace is declared in the
root ``pyproject.toml``:

.. code-block:: toml

   [tool.uv.workspace]
   members = [
       "newclid",
       "ncdgen",
       "yuclid",
   ]

Running ``uv sync`` from the repository root installs all three packages in
editable mode, including building the Yuclid C++ extension.

``newclid/``
------------

The main Python solver package and command-line entry point (``newclid =
newclid.__main__:main`` in ``newclid/pyproject.toml``). It contains:

- ``newclid/src/newclid/`` — the library: problem parsing (JGEX and GeoGebra
  input), the symbolic representation of points/lines/circles, predicates and
  rules, the pure-Python rule matcher and algebraic deductors, deductive
  agents, and proof writing/output.
- ``newclid/tests/`` — the pytest suite for the library (see
  :doc:`testing_strategy`).
- ``newclid/problems_datasets/`` — example problem files used by tests and the
  CLI.

``newclid`` depends only on pure-Python packages by default. Yuclid support is
an optional extra (``newclid[yuclid]``), which pulls in ``py-yuclid``.

``yuclid/``
-----------

The C++ deduction/matching engine, exposed to Python as the ``py_yuclid``
package. This is where the generic rule matcher documented under
:doc:`yuclid/index` lives. Its layout:

- ``yuclid/src/`` — the C++ engine: problem representation, statements,
  algebraic reasoning (``ar/``), the parser (``parser/``), rule schemas
  (``rules/``), and the matchers (``matchers/``), including the generic rule
  matcher, predicate providers, and the lazy geometry cache. Built as the
  ``yuclid`` executable plus a library, configured by ``yuclid/CMakeLists.txt``
  and ``yuclid/src/CMakeLists.txt``.
- ``yuclid/python/py_yuclid/`` — the Python bindings and adapter
  (``yuclid_adapter.py``, ``omni_matcher.py``, ``api_default.py``) that let
  ``newclid`` call the compiled ``yuclid`` executable as its rule
  matcher/deductor backend.
- ``yuclid/test/`` — C++ unit tests (Boost.Test, run through CTest) plus the
  ``.txt`` problem fixtures they exercise (``imo_ag_30/``, ``ratio_only/``,
  ``no_crash/``, ``simple/``).
- ``yuclid/tests/`` — Python integration tests that exercise ``py_yuclid``
  end to end (pytest).
- ``yuclid/cmake/``, ``yuclid/vcpkg.json`` — build tooling and dependency
  manifests.

The package is built with `scikit-build-core
<https://scikit-build-core.readthedocs.io/>`_ and CMake, as declared in
``yuclid/pyproject.toml`` (``[tool.scikit-build]``, ``build-system.requires =
["scikit-build-core", "pybind11"]``). ``py-yuclid`` depends on ``newclid`` (via
the workspace), never the other way around: ``newclid`` only imports
``py_yuclid`` lazily and optionally, at runtime, if it happens to be
installed. See :doc:`yuclid/setup` for local build instructions and
:doc:`yuclid/modules/build_and_packaging` for packaging details (static
linking, Windows Boost discovery, wheel building).

``ncdgen/``
-----------

A companion tool for generating plane-geometry diagram datasets using
Newclid (``ncdgen/src/ncdgen/``, CLI entry point ``ncdgen =
ncdgen.__main__:main``). It depends on ``newclid[yuclid]`` and is a consumer
of the solver in the same way any other downstream project would be, just
kept in-tree because it is maintained by the same team. Its tests live in
``ncdgen/tests/``.

``docs/``
---------

This Sphinx manual. ``docs/manual/`` holds the hand-written developer and user
guide (the page you are reading is part of it); ``docs/source/`` (referenced
from ``docs/index.rst``) is generated API reference documentation, produced by
``docs/reformat.py`` running ``sphinx-apidoc`` and rendered via
``sphinx.ext.autodoc``, for ``newclid``, ``yuclid``, and ``ncdgen``.

Everything else at the top level
--------------------------------

The remaining top-level files configure the workspace as a whole rather than
belonging to any one package: the root ``pyproject.toml`` (workspace
membership, shared dev dependencies, ``ruff``/``mypy``/``pytest`` settings),
``uv.lock``, ``.readthedocs.yaml`` (documentation builds), and CI workflows
under ``.github/``.
