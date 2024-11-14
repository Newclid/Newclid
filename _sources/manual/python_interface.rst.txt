Python interface
----------------

Newclid's interface is made of two main elements.

First :class:`geosolver.GeometricSolver` that contains all high level logic for the
solver to run and write outputs.

Second is :class:`geosolver.GeometricSolverBuilder` that allows to build 
a :class:`geosolver.GeometricSolver` with custom elements 
(specific problem, definitions, rules).

Below is a minimal example that uses a :class:`geosolver.GeometricSolverBuilder` to 
load a specific problem,
then uses the built :class:`geosolver.GeometricSolver` to solve it:

.. code:: python

    from geosolver import GeometricSolverBuilder, GeometricSolver

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

More examples of problems to be written can be found under the ``examples`` folder of the source repository.
More examples can also be found in ``tests``.
