Overview
========

.. role:: red
.. role:: orange
.. role:: green

Here is an overview of the main components of GeoSolver:

.. raw:: html

   <object data="../_static/Images/overview.svg" type="image/svg+xml"></object>



Deductive Agent
---------------


One can choose to run the problems either using an automatic agent
(default is :ref:`Breadth first search`, the original from AlphaGeometry work),
or a manually guided helper (:ref:`Human agent`).

The :orange:`Deductive Agent` will interact with the proof state through the :ref:`Agents interface`.
Given a :red:`Feedback` from the proof and its internal state, 
the agent outputs an :red:`Action` that will update the proof state.

After each interaction, the  :orange:`Deductive Agent` will remember it 
and update its internal state for future actions.

More detailed information on the deductive agents is available at :ref:`Agent`.


Proof State
-----------

The :green:`Proof State` is the main body of GeoSolver, 
it allows to build a proof step by step.
Each :red:`Action` type will trigger a different kind of step (apply, match, aux, ...),
and each step will use sub-components of the :green:`Proof State` that represent its internal state.

The main sub-components of the :green:`Proof State` are listed here:

- :ref:`Symbols Graph` stores all symbols (Points, Lines, Circles, Angles, ...)
  and their potential equalities.
- :ref:`Adder` is used to apply different dependency deductions 
  respectively to the :ref:`Predicates` of the added statement.
- :ref:`Checker` and :ref:`Enumerator` are used for :ref:`Match theorems`.
- :ref:`Reasoning Engines` like :ref:`Algebraic Manipulator` and :ref:`Formulas`
  allow for more powerful statements deductions than simple rule-based applications.
- :ref:`Why Graph` stores all discovered statements and their dependency (why are they true).
- :ref:`Trace Back` uses the :ref:`Dependencies` to build and print the final proof.



How is a Problem Built
----------------------

With given problem (as text or from a file), 
newclid will load the definitions (default to src/default_configs/defs.txt)
and the rules to be used (default to src/default_configs/rules.txt). 

Next, the builder will construct the problem itself.
This means compiling the information of the problem in two directions: 
the symbolic statements (proof state, dependency graph, and symbols graph)
and the numerical representation (numerical coordinates of points).

Symbolically, the builder checks if the symbolic conditions for each definition are satisfied, 
and adds the predicates assigned to each point to the proof state.

The numerical representation is built by calling the functions on the :ref:`Sketch` module.
It will then be used in the construction of the pictures in the problem, 
but also for checking numerically for some predicates 
(non-collinearity, non-parallelism, non-perpendicularity, different points).
Specifically, when building a problem, the goal will numerically check to validate the problem.

This serves two purposes:

1. A sanity check for the user, that tells if the problem is well-written or not.
2. the construction functions have intrinsic degrees of freedom, some of which may not be compatible with the problem (non-degeneracy conditions).
   If one of those is randomly hit by a construction, the goal will not be satisfied and the builder will start building again from scratch.
   This will be attempted a fixed number of times (max_attempts) before the program decides that the goal is not reacheable, 
   on the assumption that the probability of a failure at random is low.



Writing the Proof
------------------

Once the goal statement is check symbolically by the solver, 
in general it will have covered a wide graph of statements that do not necessarily contribute to the proof.
To have a clean and coherently written proof, the newclid uses a traceback, 
that tries to find the shortest straight path from the premises to the goal through the proof graph
(for more details see :ref:`Trace back`).

To be able to keep track of the connection between the steps taken on the graph, 
an important part of the proof construction is the dependency structure, 
that assigns to each statement a list of reasons for why that statement was added to the graph.
More info on :ref:`Dependencies`.


Translating to natural language
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After the traceback structures the proof, 
the predicates are translated into (pseudo) natural language by a script
(see :ref:`Proof writing` and :ref:`Pretty`). 

The written proof constains the hypothesis ("From theorem premises"), 
which are the points effectively present in the goal, 
intermediary points ("Auxiliary Constructions") used in the proof, 
and the proof steps.

Constructions given in the statement of the problem but that do not show up in the proof will not be present.

Each proof step lists the premises used for the step, the consequence,
and the reason (dependency) that makes it true.
All steps are numerated to help follow the proof.
