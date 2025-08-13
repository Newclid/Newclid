Building a problem setup
========================

Currently, Newclid supports two ways of building a problem setup:

- Translate the problem into a JGEX string (see :ref:`JGEX setup`).
- Create a GeoGebra model of the problem and adjust hypothesis and goals using Newclid's predicates (see :ref:`Geogebra setup`).

Typically, you will encounter (or create) a geometric problem using some sort of natural language, and you want to see if you can solve it using Newclid.

It is important to mention that not all geometry problems imaginable can be processed by Newclid.
Sometimes you may find limitations related to the language (concepts that cannot be expressed by the predicates/ definitions available).

Sometimes problems are overdetermined, meaning some points may need too many constraints to be defined by JGEX strings.
This prevents from easily assigning coordinates to them and in that case the problem will not build.
If that is the case, you can currently try to propose a working diagram on GeoGebra and add the needed hypothesis afterwards, but sometimes that may not be possible.

Also, keep in mind that even if a problem can be translated and built, it may still need a tool or theorem not yet implemented in Newclid for its solving, or need auxiliary points for a solution to be found.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   jgex/index
   geogebra
