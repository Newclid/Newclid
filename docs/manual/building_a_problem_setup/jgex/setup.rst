JGEX setup
==========

Generically, this refers to the vocabulary both of the predicates (see :ref:`Newclid Predicates`), and of the JGEX definitions (see :ref:`JGEX definitions`).
This allows to create the predicate assumptions and point coordinates for the problem iteratively by "Clauses" that define one or more points using a single or an intersection of constructions from the definitions.

The materialization of a translation of a problem using JGEX is a string of clauses, auxiliary clauses (that may or may not be used to build the problem) and goals.


Writing a new problem
---------------------

A translation of a problem to JGEX can look like the following:

::

   a b c = triangle a b c; d = on_tline d b a c, on_tline d c a b; e = on_line e a c, on_line e b d ? perp a d b c


`triangle`, `on_tline` and `on_line` are `definitions` (see :ref:`JGEX definitions`). 
`perp` is a predicate (see :ref:`Newclid Predicates`) used for Newclid's statements, which is used to prescribe the goal of the problem.

This problem could be read in natural language as:
    - `a b c = triangle a b c` : Let a, b and c be three points in a triangle.
    - `d = on_tline d b a c, on_tline d c a b` : Let d be the point at the intersection of DB such that DB ⟂ AC with DC such that DC ⟂ AB.
    - `e = on_line e a c, on_line e b d` : Let e be the point at the intesection of AC and BD.
    - `? `: Now prove that
    - `perp a d b c` : AD ⟂ BC

Each of the snippets of the list above before the ``?`` corresponds to a clause.
Each clause creates coordinates for the points enunciated before the ``=`` sign using `sketch` functions, as well as adds some predicate hypothesis to the problem.

To be able to translate problems from natural language to JGEX, the main effort one has to do is to get familiar with the definitions.
We provide documentation for the definitions, and after some struggle writing the first problems, you find out it is easy to get used to the vocabulary.
Also, we encourage you to compare the problems provided in the ``imo.txt`` and ``imo_sl.txt`` problem sets with their natural language versions, that can be easily found online, to learn quickly about how the definitions work.

Ensuring the problem can be built
---------------------------------

When you write a problem in JGEX the existence of a coherent coordinate representation for all points created is not guaranteed.

Given the JGEX string, the solver will try many attempts to build the coordinates for the problem, each time numerically checking if the predicate hypothesis are satisfied.
If it cannot find a good coordinate representation within its degrees of freedom, it will raise an error.

You have to take that into account when translating the problem to a JGEX string. **Constructions must be stated in an order that allows the drawing to be made.**

The process is similar to that of building a straightedge and compass construction, although more tools are available for the definition of the problem.
Also, the translation may involve changing the order of terms presented, or even reversing a construction altogether.

Evaluating if such modifications preserve the nature of the original problem is a matter of considering which hypothesis are incorporated to the NcProblem and exercising judgement.
Sometimes there is no clear-cut way to decide if a problem was modified or simply translated into Newclid.
