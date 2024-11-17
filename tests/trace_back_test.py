# Copyright 2023 DeepMind Technologies Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Unit testing for the trace_back code."""

import pytest
import pytest_check as check

from newclid.api import GeometricSolverBuilder
import newclid.problem as pr
import newclid.trace_back as tb


class TestTraceback:
    @pytest.fixture(autouse=True)
    def setUpClass(self):
        self.solver_builder = GeometricSolverBuilder()

    def test_orthocenter_dependency_difference(self):
        solver = self.solver_builder.load_problem_from_txt(
            "a b c = triangle a b c; "
            "d = on_tline d b a c, on_tline d c a b; "
            "e = on_line e a c, on_line e b d "
            "? perp a d b c"
        ).build()

        solver.run()

        goal_args = solver.proof_state.names2nodes(solver.goal.args)
        query = pr.Dependency(solver.goal.name, goal_args, None, None)
        setup, aux, _, _ = tb.get_logs(query, solver.proof_state, merge_trivials=False)

        # Convert each predicates to its hash string:
        setup = [p.hashed() for p in setup]
        aux = [p.hashed() for p in aux]

        check.equal(
            set(setup), {("perp", "a", "c", "b", "d"), ("perp", "a", "b", "c", "d")}
        )

        check.equal(set(aux), {("coll", "a", "c", "e"), ("coll", "b", "d", "e")})
