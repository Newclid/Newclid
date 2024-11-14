imo_ag_30
=========

This is the original benchmark of problems from IMO exams from 2000 to 2022 referenced in the original AlphaGeometry success of 25/30 problem in olympiad geometry problems, and has not been modified. Names of problems are of the form "translated_imo_YEAR_pNUMBER", where YEAR corresponds to the year of the exam containing the problem and NUMBER being the problem number in that exam. The translations to the formal language were made by the authors of the original paper.

The problems actually correspond to 28 original IMO problems, as problems 2002_p2 and 2008_p1 were split into two problems each to account for multiple goals in their original formulations, a capability that was not present in the original software. The list contains all IMO geometry problems from the time range that seem to be in the scope of the formal language, with the exceptions of 2005_p1, 2007_p2, and 2013_p3. Those were possibly left out on the account of being overdetermined, a situation not well processed by the engine's builder.

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
    * - translated_imo_2000_p1
      - Yes
      - 
      - 
      - 
      - 
    * - translated_imo_2000_p6
      - 
      - Yes
      - 
      - 
      - 
    * - translated_imo_2002_p2a
      - Yes
      - 
      - 
      - 
      - 
    * - translated_imo_2002_p2b
      - Yes
      - 
      - 
      - 
      - 
    * - translated_imo_2003_p4
      - Yes
      - 
      - 
      - 
      - 
    * - translated_imo_2004_p1
      - 
      - Yes
      - 
      - 
      - 
    * - translated_imo_2004_p5
      - Yes
      - 
      - 
      - 
      - 
    * - translated_imo_2005_p5
      - Yes
      - 
      - 
      - 
      - 
    * - translated_imo_2007_p4
      - Yes
      - 
      - 
      - 
      - 
    * - translated_imo_2008_p1a
      - 
      - Yes
      - 
      - 
      - 
    * - translated_imo_2008_p1b
      - 
      - 
      - 
      - 
      - Yes
    * - translated_imo_2008_p6
      - 
      - 
      - 
      - 
      - 
    * - translated_imo_2009_p2
      - 
      - Yes
      - 
      - 
      - 
    * - translated_imo_2010_p2
      - 
      - Yes
      - 
      - 
      - 
    * - translated_imo_2010_p4
      - Yes
      - 
      - 
      - 
      - 
    * - translated_imo_2011_p6
      - 
      - 
      - 
      - 
      - 
    * - translated_imo_2012_p1
      - Yes
      - 
      - 
      - 
      - 
    * - translated_imo_2012_p5
      - 
      - Yes
      - 
      - 
      - 
    * - translated_imo_2013_p4
      - Yes
      - 
      - 
      - 
      - 
    * - translated_imo_2014_p4
      - 
      - Yes
      - 
      - Yes
      - 
    * - translated_imo_2015_p3
      - 
      - Yes
      - 
      - 
      - 
    * - translated_imo_2015_p4
      - Yes
      - 
      - 
      - 
      - 
    * - translated_imo_2016_p1
      - Yes
      - 
      - 
      - 
      - 
    * - translated_imo_2017_p4
      - Yes
      - 
      - 
      - 
      - 
    * - translated_imo_2018_p1
      - 
      - Yes
      - 
      - 
      - 
    * - translated_imo_2019_p2
      - 
      - 
      - Yes
      - 
      - 
    * - translated_imo_2019_p6
      - 
      - Yes
      - 
      - 
      - 
    * - translated_imo_2020_p1
      - 
      - Yes
      - 
      - 
      - 
    * - translated_imo_2021_p3
      - 
      - 
      - 
      - 
      - 
    * - translated_imo_2022_p4
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