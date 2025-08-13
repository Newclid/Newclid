Newclid
=======

Newclid is an open-source, easy-to-use fast solver for plane geometry problems.

.. image:: https://badge.fury.io/py/newclid.svg
  :alt: Fury - PyPi stable version
  :target: https://badge.fury.io/py/newclid

.. image:: https://static.pepy.tech/badge/newclid
  :alt: PePy - Downloads
  :target: https://pepy.tech/project/newclid

.. image:: https://static.pepy.tech/badge/newclid/week
  :alt: PePy - Downloads per week
  :target: https://pepy.tech/project/newclid


.. image:: https://github.com/harmonic-ai/newclid/actions/workflows/tests.yml/badge.svg
  :alt: Python - Tests
  :target: https://github.com/Newclid/Newclid/actions/workflows/tests.yml

.. image:: https://app.codacy.com/project/badge/Grade/93afee3e7ee8464fb70f20fa9b5bf95e
  :alt: Codacy - Grade
  :target: https://app.codacy.com/gh/LMCRC/Newclid/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade

.. image:: https://app.codacy.com/project/badge/Coverage/93afee3e7ee8464fb70f20fa9b5bf95e   
  :alt: Codacy - Coverage
  :target: https://app.codacy.com/gh/LMCRC/Newclid/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json
  :alt: CodeStyle - Ruff
  :target: https://github.com/charliermarsh/ruff


Installation
------------

Using pip
^^^^^^^^^

.. code:: bash

  pip install newclid[yuclid]


From source
^^^^^^^^^^^

.. code:: bash

  git clone https://github.com/Newclid/Newclid.git
  cd Newclid
  pip install -e .[yuclid]


Quickstart
----------

To simply solve a problem using Newclid, use the command line.

For example with a JGEX problem:

.. code:: bash

  newclid jgex --problem-id orthocenter_consequence_aux --file ./problems_datasets/examples.txt

Or with a ggb problem:

.. code:: bash

  newclid ggb --file ./notebooks/ggb_exports/incenter.ggb --goals "eqangle C B B D B D B A"


See other command line interface options with:

.. code:: bash

  uv run newclid --help
  uv run newclid jgex --help
  uv run newclid ggb --help


For more complex applications, use the Python interface.
Below is a minimal example to build a problem setup from a JGEX string, then solve it:

.. code:: python

    from newclid import GeometricSolverBuilder, GeometricSolver
    import numpy as np

    # Set the random generator
    rng = np.random.default_rng()

    # Build the problem setup from JGEX string
    problem_setup = JGEXProblemBuilder(rng=rng).with_problem_from_txt(
      "a b c = triangle a b c; "
      "d = on_tline d b a c, on_tline d c a b; "
      "e = on_line e a c, on_line e b d "
      "? perp a d b c"
    ).build()

    # We now build the solver on the problem
    solver: GeometricSolver = GeometricSolverBuilder().build(problem_setup)

    # And run the solver
    success = solver.run()

    if success:
        print("Successfuly solved the problem! Proof:")
        solver.write_proof_steps()
    else:
        print("Failed to solve the problem...")

    print(f"Run infos {solver.run_infos}")

In the ``notebooks`` folder you will find more tutorials, for example:

- The Jupyter tutorial notebook ``geogebra_problems.ipynb`` to run and solve a problem from a ggb file.
- The Jupyter tutorial notebook ``jgex_problems.ipynb`` to run and solve a problem from a JGEX string.
- The Jupyter tutorial notebook ``multiple_JGEX_problems.ipynb`` to run and solve problems from a file with multiple JGEX problems, one at a time or in bulk.
- The Jupyter tutorial notebook ``heuristics_implementation.ipynb`` to run a collection of problems and try to solve them using human-made heuristics to add auxiliary points to a problem.

You can also check ``tests`` to see some more advanced examples of scripts using the Python interface.

Documentation
-------------

See `the online documentation <https://newclid.github.io/Newclid/>`_
for more detailed information about Newclid.


Contributing
------------

1. Clone the repository

.. code:: bash

  git clone https://github.com/Newclid/Newclid.git
  cd Newclid

2. Install uv

Follow `installation instructions <https://docs.astral.sh/uv/getting-started/installation/>`_

3. Install as an editable package with dev requirements

.. code:: bash

  uv sync

4. Install pre-commit and pre-push checks

.. code:: bash

  pre-commit install -t pre-commit -t pre-push


5. Run tests

.. code:: bash

  pytest tests


About Newclid
-------------------

Newclid is a successor to AlphaGeometry, introduced in this early 2024 Nature paper:
`Solving Olympiad Geometry without Human Demonstrations
<https://www.nature.com/articles/s41586-023-06747-5>`_. whose original codebase can be found `here <https://github.com/google-deepmind/alphageometry>`_.

If you found Newclid useful, please cite us as:

.. code:: bibtex

  @article{newclid2024sicca,
    author  = {Sicca, Vladmir and Xia, Tianxiang and F\'ed\'erico, Math\"is and Gorinski, Philip John and Frieder, Simon and Jui, Shangling},
    journal = {arXiv preprint},
    title   = {Newclid: A User-Friendly Replacement for AlphaGeometry with Agentic Support},
    year    = {2024}
  }


The AlphaGeometry checkpoints and vocabulary are made available
under the terms of the Creative Commons Attribution 4.0
International (CC BY 4.0) license.
You can find details at:
https://creativecommons.org/licenses/by/4.0/legalcode

