
GeoSolver: Symbolic solver for Geometric problems
=================================================

An extension of the geometric solver introduced in the Nature 2024 paper:
`Solving Olympiad Geometry without Human Demonstrations
<https://www.nature.com/articles/s41586-023-06747-5>`_.


.. image:: ../docs/_static/AlphaGeometryMainPicture.svg
  :alt: Where a geometric problem is fed to a solver (DDAR)
        and helped by an LLM to build auxiliary constructions.


AlphaGeometry can be seen as an extension of GeoSolver equipped with a language model 
that proposes new auxiliary constructions if a problem gets stuck. 

Currently new auxiliary constructions can only be added in Geosolver as human suggested 
constructions if the HumanAgent is used instead of BFSDDAR (default).


Installation
------------

Using pip
^^^^^^^^^

.. code:: bash

  pip install 'newclid>=2,<3'


From source
^^^^^^^^^^^

.. code:: bash

  git clone https://github.com/LMCRC/Newclid.git
  pip install -e . 


Quickstart
----------

To simply solve a problem using newclid, use the command line:

.. code:: bash

  newclid --problem path/to/problem:problem_name


For example:

.. code:: bash

  newclid --problem problems_datasets/examples.txt:orthocenter_consequence_aux


See other command line interface options with:

.. code:: bash

  newclid --help 

For more complex applications, use the python interface.
Below is a minimal example to load a specific problem,
then uses the built solver to solve it:

.. code:: python

    from newclid import GeometricSolverBuilder, GeometricSolver

    solver_builder = GeometricSolverBuilder()
    solver_builder.load_problem_from_txt(
        "a b c = triangle a b c; "
        "d = on_tline d b a c, on_tline d c a b "
        "? perp a d b c"
    )

    # We now obtain the GeometricSolver with the build method
    solver: GeometricSolver = solver_builder.build()

    # And run the GeometricSolver
    success = solver.run()

    if success:
        print("Successfuly solved the problem!")
    else:
        print("Failed to solve the problem...")

    print(f"Run infos {solver.run_infos}")


Some more advanced examples of script using the python interface 
are displayed in the folder ``examples`` or used in ``tests``.


Documentation
-------------

See `the online documentation <https://lmcrc.github.io/Newclid/>`_
for more detailed informations about newclid.


Contributing
------------

1. Clone the repository

.. code:: bash

  git clone https://github.com/LMCRC/Newclid.git
  cd path/to/repo

2. (Optional) Create a virtual environment, for example with venv:

.. code:: bash

  python -m venv venv

  # On UNIX
  source ./bin/activate

  # On Windows
  .\venv\Scripts\activate


3. Install as an editable package with dev requirements

.. code:: bash

  pip install -e .[dev]


4. Install pre-commit and pre-push checks

.. code:: bash

  pre-commit install -t pre-commit -t pre-push


5. Run tests

.. code:: bash

  pytest tests


About AlphaGeometry
-------------------

See `original repository <https://github.com/google-deepmind/alphageometry>`_.

.. code:: bibtex

  @Article{AlphaGeometryTrinh2024,
    author  = {Trinh, Trieu and Wu, Yuhuai and Le, Quoc and He, He and Luong, Thang},
    journal = {Nature},
    title   = {Solving Olympiad Geometry without Human Demonstrations},
    year    = {2024},
    doi     = {10.1038/s41586-023-06747-5}
  }


The AlphaGeometry checkpoints and vocabulary are made available
under the terms of the Creative Commons Attribution 4.0
International (CC BY 4.0) license.
You can find details at:
https://creativecommons.org/licenses/by/4.0/legalcode

