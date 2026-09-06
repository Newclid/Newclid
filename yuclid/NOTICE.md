Yuclid - NOTICE
===============

Yuclid is written by Yury Kudryashov (C++ engine)
and AutoMathis (python interface) for Concordance Inc. dba Harmonic.

Licensed under the Apache License, Version 2.0.
You must preserve this NOTICE in redistributions.

MODIFICATIONS
=============

Copyright 2026 Simeon Vutov, Petar Iliev

This distribution includes modifications to Yuclid made in 2026 as part of a
TU Delft Computer Science and Engineering Software Project focused on extending
Newclid.

The modifications include, at a high level:

- support for loading additional user-defined rule files at runtime;
- command-line and configuration support for passing additional rule files into
  Yuclid theorem matching and DDAR solving modes;
- separation of ordinary problem parsing from custom rule parsing;
- parsing and validation of custom Yuclid rule schemas, including rule
  variables, premises, conclusions, predicate names, and predicate arities;
- construction of Yuclid statements and theorem candidates from custom rule
  predicates and concrete point mappings;
- integration of a generic custom-rule matcher into the existing theorem
  matcher, without replacing the original hard-coded matchers;
- integration of accepted custom-rule theorem candidates into the existing
  DDAR solver pipeline;
- rule planning for custom rules, including predicate metadata, predicate
  ordering, unsupported-predicate handling, and separation of candidate
  generation from validation;
- optimized generic matching using backtracking, partial point mappings,
  candidate pruning, mapping snapshots, and rollback;
- lazy geometry caches and bucket utilities for reusable point-pair indexes,
  equal-length segment buckets, and line-orientation buckets;
- a predicate provider architecture with a registry, fallback provider, and
  predicate-specific providers for optimized candidate generation and checking;
- Python adapter support inside Yuclid for writing custom rule files, invoking
  Yuclid with those files, and resolving returned custom-rule deductions;
- build and packaging updates for the expanded Yuclid source tree, dynamic
  linking by default, Windows Boost discovery, runtime dependency installation,
  and cross-platform execution;
- tests for custom rule parsing, schema validation, statement construction,
  theorem construction, rule planning, mapping and filter state, geometry
  caches, predicate providers, generic matching, and custom-rule integration.

THIRD-PARTY SOFTWARE NOTICES
============================

The yuclid executable, when built with static linking enabled, incorporates the
GNU C Library (glibc), which is licensed under the GNU Lesser General Public
License version 2.1 (LGPL-2.1).

The LGPL-2.1 license text is available at:
https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html

The glibc source code can be obtained from: https://www.gnu.org/software/libc/

As required by Section 6 of the LGPL, the complete source code for yuclid is
provided in this distribution, allowing users to modify the Library and relink
to produce a modified executable containing the modified Library.

--------------------------------------------------------------------------------

The yuclid component incorporates pybind11, which is licensed under the
BSD 3-Clause License:

Copyright (c) 2016 Wenzel Jakob <wenzel.jakob@epfl.ch>, All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

