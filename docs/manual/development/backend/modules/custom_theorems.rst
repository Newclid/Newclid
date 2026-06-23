Backend custom theorems
=======================

Custom theorems let the frontend submit additional rule schemas with a solver
job. The backend validates the submitted payload, converts it into Newclid rule
fields, and passes the resulting rules to the solver builder.

Backend custom theorem request model
------------------------------------

The public request model is ``CustomTheoremRequest`` in ``schemas.py``. It has
four fields:

.. list-table::
   :widths: 24 26 50
   :header-rows: 1

   * - Field
     - Type
     - Meaning
   * - ``name``
     - string
     - Unique rule id for this job.
   * - ``description``
     - string
     - Human-readable rule description.
   * - ``premises``
     - list of strings
     - Predicate assumptions required by the theorem.
   * - ``conclusions``
     - list of strings
     - Predicate conclusions produced by the theorem.

The full cross-component contract is :doc:`../../contracts/custom_theorem_contract`.

Backend custom theorem validation
---------------------------------

Backend validation rejects:

- empty names;
- names longer than 100 characters;
- names that contain spaces or unsupported punctuation;
- empty premise or conclusion lists;
- empty predicate lines;
- multi-line predicate strings;
- duplicate custom theorem names within one job request.

These checks are API-level checks. Predicate semantics are still handled by
Newclid when the runner constructs ``Rule`` objects.

Backend custom theorem conversion
---------------------------------

``runner_helpers.py`` converts the public request dictionaries to Newclid rule
keyword arguments:

.. code-block:: text

   name         -> id
   description  -> description, or name if empty
   premises     -> premises_txt
   conclusions  -> conclusions_txt

Then ``newclid_runner.py`` constructs ``Rule`` objects and passes them to
``GeometricSolverBuilder.with_additional_rules``.

Backend custom theorem ownership
--------------------------------

The backend is responsible for transport validation and conversion. It should
not implement a second rule parser. The actual rule interpretation belongs in
Newclid and Yuclid's generic matcher stack.
