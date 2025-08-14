imo_ag_30
=========

This is the original benchmark of problems from IMO exams from 2000 to 2022 referenced in the original AlphaGeometry success of 25/30 problem in olympiad geometry problems, and has not been modified. Names of problems are of the form "YEAR_pNUMBER", where YEAR corresponds to the year of the exam containing the problem and NUMBER being the problem number in that exam. The translations to the formal language were made by the authors of the original paper.

The problems actually correspond to 28 original IMO problems, as problems 2002_p2 and 2008_p1 were split into two problems each to account for multiple goals in their original formulations, a capability that was not present in the original software. The list contains all IMO geometry problems from that time range that seem to be in the scope of the formal language, with the exceptions of 2005_p1, 2007_p2, and 2013_p3. Those were possibly left out on the account of being overdetermined, a situation not well processed by the engine's builder.

The table below brings a breakdown of the solvability of the problems in the imo_ag_30 benchmark with respect to the different solvers. Only the minimal amount of fields is filled, but any problem that can be solved by DDAR is solvable by Newclid as well, and problems solved with points prescribed by the LLM can obviously be solved by DDAR or Newclid if those same points are human prescribed, of course.

.. list-table::
    :widths: 30 14 14 14 14 14
    :header-rows: 1

    * - Problem Name
      - Solved w/ original DDAR?
      - Solved w/ DDAR+LLM?
      - Solved w/ Human suggested points+DDAR?
      - Solved w/ Newclid?
      - Solved w/ Human suggested points+Newclid?
    * - 2000_p1
      - Yes
      - 
      - 
      - 
      - 
    * - 2000_p6
      - 
      - Yes
      - 
      - 
      - 
    * - 2002_p2a
      - Yes
      - 
      - 
      - 
      - 
    * - 2002_p2b
      - Yes
      - 
      - 
      - 
      - 
    * - 2003_p4
      - Yes
      - 
      - 
      - 
      - 
    * - 2004_p1
      - 
      - Yes
      - 
      - 
      - 
    * - 2004_p5
      - Yes
      - 
      - 
      - 
      - 
    * - 2005_p5
      - Yes
      - 
      - 
      - 
      - 
    * - 2007_p4
      - Yes
      - 
      - 
      - 
      - 
    * - 2008_p1a
      - 
      - Yes
      - 
      - 
      - 
    * - 2008_p1b
      - 
      - 
      - 
      - 
      - Yes
    * - 2008_p6
      - 
      - 
      - 
      - 
      - 
    * - 2009_p2
      - 
      - Yes
      - 
      - 
      - 
    * - 2010_p2
      - 
      - Yes
      - 
      - 
      - 
    * - 2010_p4
      - Yes
      - 
      - 
      - 
      - 
    * - 2011_p6
      - 
      - 
      - 
      - 
      - 
    * - 2012_p1
      - Yes
      - 
      - 
      - 
      - 
    * - 2012_p5
      - 
      - Yes
      - 
      - 
      - 
    * - 2013_p4
      - Yes
      - 
      - 
      - 
      - 
    * - 2014_p4
      - 
      - Yes
      - 
      - Yes
      - 
    * - 2015_p3
      - 
      - Yes
      - 
      - 
      - 
    * - 2015_p4
      - Yes
      - 
      - 
      - 
      - 
    * - 2016_p1
      - Yes
      - 
      - 
      - 
      - 
    * - 2017_p4
      - Yes
      - 
      - 
      - 
      - 
    * - 2018_p1
      - 
      - Yes
      - 
      - 
      - 
    * - 2019_p2
      - 
      - 
      - Yes
      - 
      - 
    * - 2019_p6
      - 
      - Yes
      - 
      - 
      - 
    * - 2020_p1
      - 
      - Yes
      - 
      - 
      - 
    * - 2021_p3
      - 
      - 
      - 
      - 
      - 
    * - 2022_p4
      - Yes
      - 
      - 
      - 
      - 
    * - Total numbers
      - 14
      - 14+11
      - 14+11+1
      - 14+1
      - 14+11+1+1