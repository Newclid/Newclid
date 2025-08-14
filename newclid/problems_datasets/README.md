# What are the problems files?

**examples.txt:** Smaller problems designed during the development of Newclid, typically to test singular features. Now part of the regression tests

**imo_102_requires_aux.txt:** 102 problems from larger_imo_eval.txt that could not be solved by DDAR alone. They were used as a large benchmark for the developing of LLMs that recommend auxiliary constructions to aid DDAR solutions.

**imo_sl.txt:** Problems gathered and translated by the Harmonic team from IMO's shortlist.

**imo.txt:** Collection of IMO problems gathered for the different benchmarks, notably containing the original imo_ag_30 benchmark from AlphaGeometry. For the problems in the imo_ag_30 with aux constructions. They were either taken from the original paper (including 2019_2 suggested by humans), from Newclid's paper (2008_p1b, which contains 2008_p1a, reformulated and suggested by humans), and different points for 2020_p1 suggested by Harmonic's LLM (for a different formulation of the problem: imo_sl_2020_g2) as we could not reproduce the proof in AG's paper.

**jgex_ag_231.txt:** Original collection of simpler problems studied in the AG1 paper.

**large_examples.txt:** Larger problems previously part of examples, they were developed to check individual features of the engine or try olympiad problems. Now part of the regression tests.

**larger_imo_eval.txt:** Collection of 172 problems from old IMO exams or IMO shortlists gathered by the Harmonic and Newclid teams in the past. This was used for a larger benchmark of problems for the new system. The ones that could not be solved by DDAR alone were filtered and added to the imo_102_requires_aux benchmark for the LLMs.

**new_problems.txt:** Collection of problems that could not be tested on the original AG1, but that could be addressed by the original development of Newclid.

**old_newclid_benchmark_50.txt:** Collection of IMO shortlist problems that were part of the new_benchmark_50 from the original Newclid codebase, but with the JGEX formulations made by the Newclid team.

**testing_minimal_rules.txt:** Collection of small problems meant to test one rule at a time. Part of the regression tests.

**usamo.txt:** Collection of problems from the USAMO that were used to build different benchmarks for Newclid.
