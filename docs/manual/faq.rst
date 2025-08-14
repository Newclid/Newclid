Frequently Asked Questions
==========================

How to run a problem?
---------------------

Given a problem already turned into a ggb file, or translated into a JGEX string, or given a list of problems translated into JGEX in a file, you have a couple of ways to run that problem.

In the ``notebooks`` folder you will find:

- ``imo_2025.ipynb`` to run and solve a problem from the IMO 2025 P2 problem and build the animated proof.

.. image:: https://colab.research.google.com/assets/colab-badge.svg
  :alt: Open IMO notebook in Colab
  :target: https://colab.research.google.com/github/Newclid/Newclid/blob/main/notebooks/imo_2025.ipynb

- The Jupyter tutorial notebook ``geogebra_problems.ipynb`` to run and solve a problem from a ggb file.

.. image:: https://colab.research.google.com/assets/colab-badge.svg
  :alt: Open Geogebra notebook in Colab
  :target: https://colab.research.google.com/github/Newclid/Newclid/blob/main/notebooks/geogebra_problem.ipynb

- The Jupyter tutorial notebook ``jgex_problems.ipynb`` to run and solve a problem from a JGEX string.

.. image:: https://colab.research.google.com/assets/colab-badge.svg
  :alt: Open JGEX notebook in Colab
  :target: https://colab.research.google.com/github/Newclid/Newclid/blob/main/notebooks/JGEX_problem.ipynb

- The Jupyter tutorial notebook ``multiple_JGEX_problems.ipynb`` to run and solve problems from a file with multiple JGEX problems, one at a time or in bulk.

.. image:: https://colab.research.google.com/assets/colab-badge.svg
  :alt: Open Multiple JGEX problems notebook in Colab
  :target: https://colab.research.google.com/github/Newclid/Newclid/blob/main/notebooks/multiple_JGEX_problems.ipynb

- The Jupyter tutorial notebook ``heuristics_implementation.ipynb`` to run a collection of problems and try to solve them using human-made heuristics to add auxiliary points to a problem.

.. image:: https://colab.research.google.com/assets/colab-badge.svg
  :alt: Open Heuristics implementation notebook in Colab
  :target: https://colab.research.google.com/github/Newclid/Newclid/blob/main/notebooks/heuristics_implementation.ipynb

You can also run problems from the command line.

- ``uv run newclid --help`` will give you all options available.
- ``uv run newclid jgex --help`` will show the specific syntax for JGEX problems.
- ``uv run newclid ggb --help`` will show the specific syntax for ggb problems.

A typical run for a problem given as a JGEX string would be:

::
    
    uv run newclid --output-dir ninepoints --draw-final-figure jgex --problem "a b c = triangle a b c; m = midpoint m a b; n = midpoint n b c; p = midpoint p a c; f1 = foot f1 a b c; f2 = foot f2 b a c; f3 = foot f3 c a b ? cyclic m n p f1 f2 f3"

If you want to run a problem from a txt file with other problems, you can use:

::

    uv run newclid --output-dir ninepoints jgex --file ./newclid/problems_datasets/large_examples.txt --problem-id ninepoints

Or you can try to run a problem from a ggb file, in which case you should specify the goals:

::

    uv run newclid --output-dir incenter ggb --file ./newclid/notebooks/ggb_exports/incenter.ggb --goals "eqangle c b b d b d b a"


What are the structures that correspond to geometric concepts?
--------------------------------------------------------------

There are multiple ways Newclid represents geometric concepts:

- Geometric objects are encoded in different ways, either as classes or types and either globally or for specific modules. See :ref:`What are the geometric objects in the code?` below. We have representations for points, lines, circles, segments, ratios, angles, and triangles.

- :ref:`Newclid Predicates` which are Python classes that represent relations between geometric objects, such as Perpendicular, Parallel, Collinear, etc.

- :ref:`Rules` which correspond to geometric theorems.

- :ref:`JGEX definitions` which correspond to JGEX geometric constructions that add points and predicates to the building of the problem.

What are the geometric objects in the code?
-------------------------------------------

The most fundamental geometric object in the engine are points. In principle, all other objects, predicates, rules, and definitions depend on points to exist. They are encoded in two basic classes:

- PointNum: that carries their coordinates and functions that allow for geometric manipulations (see :doc:`../source/newclid.numerical.geometries`).
- Point: that is stored in the SymbolsRegistry for symbolic (logical) reasoning (see :doc:`../source/newclid.symbols.points_registry`).

Similar to points, although not externally influenced, the engine also executes reasoning with Lines and Circles, with corresponding classes :doc:`LineNum <../source/newclid.numerical.geometries>`, :doc:`LineSymbol <../source/newclid.symbols.lines_registry>`, :doc:`CircleNum <../source/newclid.numerical.geometries>`, and :doc:`CircleSymbol <../source/newclid.symbols.circles_registry>`.

Lines, circles, and points will be stored in their respective components of the :doc:`SymbolsRegistry<../source/newclid.symbols.symbolsregistry>` class. On top of that, the registries of lines and circles also carry information about `merging` operations, which are those that recognize that two lines or two circles actually have the same points, and hence are the same. That recognition is obtained from collinear and concyclic statements, respectively.

Another global presence of geometric objects is as types corresponding to predicate arguments. Although they boil down to collections of elements of the Point class (tuples or tuples of tuples), the following types are used as arguments in predicates, instead of bare points: Segment, Ratio, Line, Angle, and Triangle (see :doc:`../source/newclid.symbols.points_registry`).

How can I add new definitions?
------------------------------

Definitions are placed in the different modules of ``jgex/constructions`` (``complete_figure``, ``free``, ``intersections``, ``point_on_object``, ``predicate_presriptions``, ``problem_specific``, ``relative_to``). After choosing a module, you have to add an instance of the ``JGEXDefinition`` class with the attributes you expect from your construction, as well as a corresponding sketch function to ``jgex/sketch.py``. Finally, to be recognized, the definition should be listed in the ``JGEXCOnstructionName`` class in the ``jgex/constructions/__init__.py`` file.

How can I add new rules?
------------------------

Currently, rules cannot be added to Newclid alone, as the proof is processed by Yuclid. A new rule would have to be added both on Newclid's all_rules.py and on Yuclid, where it has to be associated to a matching function and processed in the C++/Python bridges. In Newclid, a rule entry has to be added to the all_rules.py file, to the ALL_RULES list, and a test should be added to tests/test_individual_rules.py.

What do I get after I run a problem?
------------------------------------

After succesfully running a problem, the engine generates a series of outputs from it, that provide information on the run, the solution, and clarify the logical reasoning that was performed. The outputs are:

- Run infos: it tells you basic metadata about the proof, such as the time it took to run in seconds, if it was succesful in general and for each goal, and how many reasoning steps it took to teach the conclusion (typically more than the steps effectively used in the proof). It also gives some technical information from the deductive agent.

- The proof text: the actual content of the proof, with all the information needed to understand the process taken by the engine (better described :ref:`here<How is the proof structured?>`). The proof can be displayed in the screen, saved as a text file, or displayed as an animations, as you can see in the tutorial notebooks.

- The predicates graph: a graph that shows the proof steps not linearly, but as a graph of justifications between steps of the proof. Basically, it links each predicate in the proof to the previous predicates that were used to prove it (see :ref:`What are justifications?` below). The information is always stored after the engine runs a problem, but to get a structured visualization you must ask for the outputs of to be saved in a folder, in which case it will be saved inside the `html` subfolder.

- Two images of the proof: `proof_figure.svg` contains all the drawings of all the steps of the proof compactified in one image, the animation is a better way to understand what is happening here. Inside the `html` folder you'll find a file called `geometry.svg`, which contains the initial constructions of the problem, before any reasoning was applied. Both images are generated and exported to the output folder, if required by the user.

- The animation: you can also generate an animation of the proof constructions and proof steps, which can either turn into a step-by-step visualization of the proof, a gif, or an `.mp4` video. The animation has to be explicited generated, as you can see in the tutorial notebooks.

How is the proof structured?
----------------------------

The proof generated by the engine is structured in steps meant to be human-readable, but also sufficiently detailed for anyone who wants to check that the machine is functioning correctly and allow reproducibility of results. The information contained is not generated by an LLM, but rather it is scripted, hence a bit mechanical. The animation is certainly the best companion for anyone wanting to actually understand the mathematical ideas behind the proof.

The proof is divided as follows:

- The "Problem setup" contains the coordinates of the points used in the problem as well as the hypothesis provided to the engine. It also lists the "Numerical checks" that were extracted from the point configuration and that are used by some theorem at some step of the proof.

- The "Goals" of the problem, including if each of them was solved or not, and if yes it tells you at which step of the proof it was solved.

- The "Proof" contains all the proof steps of the logical reasoning. Each step should hold by itself, in the sense that the hypothesis provided by the step should give the conclusion of the step by the reason described in the arrow. The numbering of all hypothesis, numerical checks, and conclusions also allows one to locate where each hypothesis was generated in the body of the proof.

- The "Appendix" brings the description of the linear system behind each AR Deduction step, and describes the relevant steps of the Gaussian elimination procedure taken to get the result. It tells you how each linear equation is formed from the corresponding logical predicate, including the coefficients of each variable in the equation, and each operation performed to get new equations, until the last line, when an equation is turned into the corresponding logical predicate.

What are justifications?
------------------------

A justification is the reason a given predicate is true and was added to the proof.
In the current code, it can be the application of a rule, an algebraic reasoning step (angle chasing or ratio chasing), a numerical check, a construction, or the recognition that two lines or two circles are the same in the Symbols Registry (a *merge* operation).
Justifications store the information needed to perform the traceback to extract the proof from the full collection of statements proved, to tie the proof steps, to build the predicates graph, and to generate the animation.

What is the proper way to add an auxiliary point to a problem?
--------------------------------------------------------------

Given a JGEX formulation to the problem, and the construction of the auxiliary point(s) in JGEX, append the construction to the JGEX formulation string preceeded by a " | ", before the " ? " that indicates the goal. For example, if your JGEX formulation is:

::

    a b c = triangle a b c; o = midpoint o b c; m = on_circle m o b, on_line m a b; n = on_circle n o b, on_line n a c; r = angle_bisector r b a c, angle_bisector r m o n; o1 = circle o1 b m r; o2 = circle o2 c n r; p = on_circle p o1 r, on_circle p o2 r ? coll p b c

You can add auxiliary points ``k`` and ``l`` by writing

::

    a b c = triangle a b c; o = midpoint o b c; m = on_circle m o b, on_line m a b; n = on_circle n o b, on_line n a c; r = angle_bisector r b a c, angle_bisector r m o n; o1 = circle o1 b m r; o2 = circle o2 c n r; p = on_circle p o1 r, on_circle p o2 r | k = on_bline k m n; l = eqdistance l k k a, eqdistance l o o a ? coll p b c

Then, when calling the ``JGEXProblemBuilder`` method to build the problem, you can pass the ``.include_auxiliary_clauses(True)`` method to include the auxiliary points in the problem. Or ``.include_auxiliary_clauses(False)`` if you do not want to include the auxiliary point in this build.
