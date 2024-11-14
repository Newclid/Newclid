Adding new problems
===================

Using definitions
-----------------

The language used to state problems is that of the definitions.
The default definitions used can be found in ``default_configs/defs.txt`` as an example.

Each definition is composed of a block of 5 lines divided in the following way:

1. Signature of the definition (name and expected arguments).
2. Dependency between elements being created and the other arguments, separated by a ":". 
   If it is to be used for intersecting, the point created should be present on both sides of the colon.
3. Arguments that should be existing points in the definition, 
   on the left-hand side, and symbolic conditions they must satisfy for validity, 
   on the right-hand side, separated by a "=".
   If the line is simply " = ", no previous points are needed for the definition.
4. Lists the points created and the symbolic predicates to be assigned to each. 
   Each new point has to be defined by one definition or two in the case of an intersection.
5. Function to be called in the sketch module to add the created points 
   to the numerical representation of the problem, with the proper arguments.


Some definitions can be used in combination with others 
(stated in the definition of a point with a separation by ","), 
as intersections of geometric elements.

Writing a new problem
---------------------

Once definitions are set up, problems can be written as such:

::

   a b c = triangle; d = on_tline d b a c, on_tline d c a b; e = on_line e a c, on_line e b d ? perp a d b c


`triangle`, `on_tline` and `on_line` would be definitions specified for example in defs.txt.
`perp` is a predicate used for Newclid's statements (See their list at :ref:`Predicates`).

This problem could be read in natural language as:
    - `a b c = triangle` : Let a, b and c three points in a triangle.
    - `d = on_tline d b a c, on_tline d c a b` : Let d be the point 
      such that it is at the intesection of DB such that DB ⟂ AC and of DC such that DC ⟂ AB.
    - `e = on_line e a c, on_line e b d` : Let e be the point at the intesection of AC and BD.
    - `? perp a d b c` : Prove that AD ⟂ BC.

Ensuring the problem can be built
---------------------------------

In order to write a problem, 
a numerical diagram representation for it must be built alongside.

**Thus constructions must be stated in an order that allows the drawing to be made.**

The process is similar to that of building a straightedge and compass construction, 
although more tools are available for the definition of the problem. 

This translation may involve changing the order of terms presented, 
or even reversing a construction altogether.

Still, some problems may not be written into the Newclid for being overdetermined,
or may demand the offering of extra information to the solver, such as extra points,
with respect to its original statement.

To evaluate if such modifications preserve the nature of the original problem 
is a matter of considering which facts/predicates are offered to the solver 
as hypothesis and exercising judgement. Sometimes there is no clear-cut way to decide if a problem was modified 
or simply translated into Newclid.

When giving a problem to the solver, the problem, definitions to be used, 
and set of rules to be assumed in the derivation can be given in dedicated .txt files 
with the proper formatting, or as strings directly in the builder function.

