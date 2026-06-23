Frontend setup
==============

Prerequisites
-------------

- **Node.js 18+** and **npm** (bundled with Node).
- The Newclid backend running locally on port ``8000`` (optional for pure UI work, required to submit proofs).

Install
-------

From the repository root:

.. code-block:: bash

   cd frontend
   npm install

Running the dev server
----------------------

.. code-block:: bash

   npm run dev

Vite starts on `<http://localhost:5173>`_ and opens the browser automatically.
API requests to ``/api`` are proxied to ``http://localhost:8000``, so the backend is transparent to the frontend code.

Type checking
-------------

.. code-block:: bash

   npm run typecheck

Runs ``tsc --noEmit`` without emitting any files.
Run this before committing to catch type errors.

Production build
----------------

.. code-block:: bash

   npm run build

Output goes to ``frontend/dist/``.
The backend serves this directory in production.
