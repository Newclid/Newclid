Yuclid build and packaging
==========================

The custom-rule matcher adds new C++ files and adjusts packaging behavior so the
Yuclid executable can be built and used consistently across local development,
Python packaging, and Windows environments.

Yuclid matcher files in CMake
-----------------------------

New matcher, parser, rule, and statement-builder files must be listed in
``yuclid/src/CMakeLists.txt``. If a future provider or cache is added but not
listed there, local tests may fail to link or the Python package may miss the
implementation.

The custom-rule work adds files under:

.. code-block:: text

   yuclid/src/matchers/
   yuclid/src/parser/
   yuclid/src/rules/
   yuclid/src/statement/

Yuclid static linking change
----------------------------

Static linking is disabled by default for this integration. This makes the build
friendlier for Python packaging and Windows runtime dependency handling. Do not
assume that the executable is fully self-contained; runtime libraries may need to
be installed next to the executable.

Yuclid Windows Boost lookup
---------------------------

On Windows, Boost may not be discoverable from a standard CMake path. The build
can use ``YUCLID_BOOST_DIR`` to point CMake at the directory containing
``BoostConfig.cmake``.

.. code-block:: text

   YUCLID_BOOST_DIR=<path-to-boost-cmake-directory>

If this variable is set but ``BoostConfig.cmake`` cannot be found there, the
build should fail early with a clear error instead of failing later during link
or runtime execution.

Yuclid runtime DLL installation
-------------------------------

When building on Windows with dynamic Boost libraries, the executable needs the
required runtime DLLs next to it. The CMake install step copies target runtime
DLLs for ``yuclid_exe`` into the same destination as the executable. This avoids
runtime crashes caused by missing DLLs.

Yuclid packaging rule
---------------------

When adding a new matcher component, update both the normal CMake build and the
Python packaging path. The Python wheel should include an executable that behaves
like the locally built executable, including support for
``--input-additional-rules-file``.
