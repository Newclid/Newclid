jgex_ag_231
===========

This is an accompanying benchmark with 231 problems to the more remarkable :ref:`imo_ag_30` from the original AlphaGeometry paper.
Unfortunately, we couldn't track its origin, if it was created specifically for the AlphaGeometry testing, or the original statements of problems.
This lack of information makes it harder to use this database to understand the engine's behavior, but problems are usually shorter than IMO ones, allowing for a faster benchmarking over many problems.
We do know some heavier definitions were clearly created to address specific problems from the jgex_ag_231 database, as they show up in the statement of a single problem and contain composed constructions (see :ref:` JGEXDefinitions`).

The sum up of results is that the original DDAR running solo solved 198/231 problems, and with the addition of LLM suggestions its performance increased to 228/231 problems. Newclid, on its hand, solved 201/231 problems.

We present a list of the problems in the jgex_ag_231 database below, making explicit which ones are solvable with the original DDAR and which ones with Newclid.

.. list-table::
    :widths: 5 55 20 20
    :header-rows: 1

    * - #
      - Problem Name
      - Solved w/ original DDAR?
      - Solved w/ Newclid?
    * - 1
      - examples--complete2--012--complete_004_6_GDD_FULL_81-109_101.gex
      - Yes
      - Yes
    * - 2
      - examples--complete2--012--complete_002_6_GDD_FULL_41-60_59.gex
      - Yes
      - Yes
    * - 3
      - examples--complete2--012--complete_002_6_GDD_FULL_01-20_04.gex
      - Yes
      - Yes
    * - 4
      - examples--complete2--012--complete_004_6_GDD_FULL_81-109_90.gex
      - Yes
      - Yes
    * - 5
      - examples--complete2--012--complete_004_6_GDD_FULL_81-109_94.gex
      - Yes
      - Yes
    * - 6
      - examples--complete2--012--complete_003_6_GDD_FULL_21-40_37.gex
      - Yes
      - Yes
    * - 7
      - examples--complete2--012--complete_003_6_GDD_FULL_21-40_22.gex
      - Yes
      - Yes
    * - 8
      - examples--complete2--012--complete_001_6_GDD_FULL_01-20_19.gex
      - Yes
      - Yes
    * - 9
      - examples--complete2--012--complete_001_6_GDD_FULL_61-80_74.gex
      - Yes
      - Yes
    * - 10
      - examples--complete2--013--complete_002_6_GDD_FULL_41-60_49.gex
      - Yes
      - Yes
    * - 11
      - examples--complete2--013--complete_006_Other_ndgTest_70.gex
      - Yes
      - Yes
    * - 12
      - examples--complete2--013--complete_001_6_GDD_FULL_01-20_16.gex
      - Yes
      - Yes
    * - 13
      - examples--complete2--013--complete_001_6_GDD_FULL_61-80_67.gex
      - Yes
      - Yes
    * - 14
      - examples--complete2--013--complete_000_2_PWW_A018.gex
      - Yes
      - Yes
    * - 15
      - examples--complete2--013--complete_004_6_GDD_FULL_81-109_88.gex
      - Yes
      - Yes
    * - 16
      - examples--complete2--013--complete_003_6_GDD_FULL_21-40_24.gex
      - Yes
      - Yes
    * - 17
      - examples--complete2--013--complete_003_6_GDD_FULL_21-40_32.gex
      - Yes
      - Yes
    * - 18
      - examples--complete2--013--complete_002_6_GDD_FULL_41-60_54.gex
      - Yes
      - Yes
    * - 19
      - examples--complete2--013--complete_005_Other_ndg1_53.gex
      - Yes
      - Yes
    * - 20
      - examples--complete2--013--complete_002_6_GDD_FULL_41-60_56.gex
      - Yes
      - Yes
    * - 21
      - examples--complete2--013--complete_002_6_GDD_FULL_41-60_52.gex
      - Yes
      - Yes
    * - 22
      - examples--complete2--014--complete_008_7_Book_LLL_L053-1.gex
      - 
      - 
    * - 23
      - examples--complete2--014--complete_007_7_Book_LLL_L058-9.gex
      - 
      - 
    * - 24
      - examples--complete2--007--complete_003_6_GDD_FULL_more_E015-6.gex
      - Yes
      - Yes
    * - 25
      - examples--complete2--007--complete_003_6_GDD_FULL_more_E022-9.gex
      - Yes
      - Yes
    * - 26
      - examples--complete2--007--complete_012_7_Book_00EE_02_E028-2.gex
      - Yes
      - Yes
    * - 27
      - examples--complete2--007--complete_012_7_Book_00EE_05_E051-22.gex
      - Yes
      - Yes
    * - 28
      - examples--complete2--007--complete_005_Other_other_E075-25-sss.gex
      - Yes
      - Yes
    * - 29
      - examples--complete2--007--complete_001_6_GDD_FULL_01-20_01.gex
      - Yes
      - Yes
    * - 30
      - examples--complete2--007--complete_000_2_PWW_B016x.gex
      - Yes
      - Yes
    * - 31
      - examples--complete2--007--complete_001_6_GDD_FULL_61-80_66.gex
      - Yes
      - Yes
    * - 32
      - examples--complete2--007--complete_016_7_Book_00EE_06_E051-30.gex
      - Yes
      - Yes
    * - 33
      - examples--complete2--007--complete_016_7_Book_00EE_06_E051-24.gex
      - Yes
      - Yes
    * - 34
      - examples--complete2--007--complete_013_7_Book_00EE_11_E077-37.gex
      - Yes
      - Yes
    * - 35
      - examples--complete2--007--complete_013_7_Book_00EE_07_E059-54-1.gex
      - Yes
      - Yes
    * - 36
      - examples--complete2--007--complete_008_ex-gao_ex160_e201f.gex
      - Yes
      - Yes
    * - 37
      - examples--complete2--000--complete_016_ex-gao_gao_M_M020-52.gex
      - Yes
      - Yes
    * - 38
      - examples--complete2--000--complete_010_Other_gao_L_L190-7.gex
      - Yes
      - Yes
    * - 39
      - examples--complete2--000--complete_007_7_Book_LLL_L017-11.gex
      - Yes
      - Yes
    * - 40
      - examples--complete2--000--complete_016_ex-gao_gao_M_M024-94.gex
      - Yes
      - Yes
    * - 41
      - examples--complete2--000--complete_007_7_Book_LLL_L054-2-1.gex
      - Yes
      - Yes
    * - 42
      - examples--complete2--000--complete_007_7_Book_LLL_L057-1-1.gex
      - Yes
      - Yes
    * - 43
      - examples--complete2--000--complete_016_ex-gao_gao_M_M021-64.gex
      - Yes
      - Yes
    * - 44
      - examples--complete2--000--complete_007_7_Book_LLL_L057-3-2.gex
      - Yes
      - Yes
    * - 45
      - examples--complete2--000--complete_004_6_GDD_FULL_81-109_95.gex
      - Yes
      - Yes
    * - 46
      - examples--complete2--000--complete_001_6_GDD_FULL_01-20_02.gex
      - Yes
      - Yes
    * - 47
      - examples--complete2--000--complete_004_6_GDD_FULL_81-109_96.gex
      - Yes
      - Yes
    * - 48
      - examples--complete2--000--complete_007_7_Book_LLL_L194-2.gex
      - Yes
      - Yes
    * - 49
      - examples--complete2--000--complete_017_ex-gao_gao_L_L022-1.gex
      - Yes
      - Yes
    * - 50
      - examples--complete2--000--complete_016_ex-gao_gao_M_M09-14.gex
      - Yes
      - Yes
    * - 51
      - examples--complete2--009--complete_014_7_Book_00EE_09_E071-4.gex
      - Yes
      - Yes
    * - 52
      - examples--complete2--009--complete_013_7_Book_00EE_10_E072-13.gex
      - Yes
      - Yes
    * - 53
      - examples--complete2--009--complete_014_7_Book_00EE_09_E071-2.gex
      - Yes
      - Yes
    * - 54
      - examples--complete2--009--complete_014_7_Book_00EE_09_E071-1.gex
      - Yes
      - Yes
    * - 55
      - examples--complete2--009--complete_017_ex-gao_ex160_4_e10.gex
      - Yes
      - Yes
    * - 56
      - examples--complete2--009--complete_003_6_GDD_FULL_more_E022-12.gex
      - Yes
      - Yes
    * - 57
      - examples--complete2--009--complete_001_6_GDD_FULL_61-80_69.gex
      - Yes
      - Yes
    * - 58
      - examples--complete2--009--complete_012_7_Book_00EE_05_E051-19.gex
      - Yes
      - Yes
    * - 59
      - examples--complete2--009--complete_016_7_Book_00EE_06_E051-32.gex
      - Yes
      - Yes
    * - 60
      - examples--complete2--009--complete_013_7_Book_00EE_10_E074-23.gex
      - Yes
      - Yes
    * - 61
      - examples--complete2--009--complete_011_Other_Auxiliary_aux2_trapezoid.gex
      - Yes
      - Yes
    * - 62
      - examples--complete2--009--complete_016_7_Book_00EE_06_E057-37.gex
      - Yes
      - Yes
    * - 63
      - examples--complete2--008--complete_004_6_GDD_FULL_81-109_100.gex
      - Yes
      - Yes
    * - 64
      - examples--complete2--008--complete_005_Other_ndgs_02.gex
      - Yes
      - Yes
    * - 65
      - examples--complete2--008--complete_008_ex-gao_ex160_205.gex
      - Yes
      - Yes
    * - 66
      - examples--complete2--008--complete_015_7_Book_00EE_08_E061-62.gex
      - Yes
      - Yes
    * - 67
      - examples--complete2--008--complete_015_7_Book_00EE_06_E051-31.gex
      - Yes
      - Yes
    * - 68
      - examples--complete2--008--complete_011_7_Book_00EE_03_E037-22.gex
      - Yes
      - Yes
    * - 69
      - examples--complete2--008--complete_011_7_Book_00EE_03_E037-21.gex
      - Yes
      - Yes
    * - 70
      - examples--complete2--008--complete_011_7_Book_00EE_04_E051-5.gex
      - Yes
      - Yes
    * - 71
      - examples--complete2--008--complete_003_6_GDD_FULL_more_E009-1.gex
      - Yes
      - Yes
    * - 72
      - examples--complete2--008--complete_011_7_Book_00EE_03_E039-28.gex
      - Yes
      - Yes
    * - 73
      - examples--complete2--008--complete_011_7_Book_00EE_03_E040-28-1.gex
      - Yes
      - Yes
    * - 74
      - examples--complete2--008--complete_018_ex-gao_ex160_4_004.gex
      - Yes
      - Yes
    * - 75
      - examples--complete2--008--complete_014_7_Book_00EE_07_E059-50.gex
      - Yes
      - Yes
    * - 76
      - examples--complete2--008--complete_013_7_Book_00EE_07_E057-44.gex
      - Yes
      - Yes
    * - 77
      - examples--complete2--001--complete_006_7_Book_LLL_L046-16.gex
      - Yes
      - Yes
    * - 78
      - examples--complete2--001--complete_016_ex-gao_gao_M_M010-32.gex
      - Yes
      - Yes
    * - 79
      - examples--complete2--001--complete_016_ex-gao_gao_M_M010-26.gex
      - Yes
      - Yes
    * - 80
      - examples--complete2--001--complete_016_ex-gao_gao_C_C101.gex
      - Yes
      - Yes
    * - 81
      - examples--complete2--001--complete_016_ex-gao_gao_C_C100.gex
      - Yes
      - Yes
    * - 82
      - examples--complete2--001--complete_016_ex-gao_gao_L_L182-6.gex
      - Yes
      - Yes
    * - 83
      - examples--complete2--001--complete_016_ex-gao_gao_C_C111.gex
      - Yes
      - Yes
    * - 84
      - examples--complete2--001--complete_016_ex-gao_gao_L_L025-5.gex
      - Yes
      - Yes
    * - 85
      - examples--complete2--001--complete_017_ex-gao_gao_L_L189-2.gex
      - Yes
      - Yes
    * - 86
      - examples--complete2--001--complete_016_ex-gao_gao_L_L182-5.gex
      - Yes
      - Yes
    * - 87
      - examples--complete2--001--complete_017_ex-gao_gao_L_L189-1.gex
      - Yes
      - Yes
    * - 88
      - examples--complete2--001--complete_016_ex-gao_gao_C_C109.gex
      - Yes
      - Yes
    * - 89
      - examples--complete2--001--complete_016_ex-gao_gao_L_LL153-1.gex
      - Yes
      - Yes
    * - 90
      - examples--complete2--001--complete_010_Other_gao_Y_yL182-4.gex
      - Yes
      - Yes
    * - 91
      - examples--complete2--006--complete_012_7_Book_00EE_02_E028-3.gex
      - Yes
      - Yes
    * - 92
      - examples--complete2--006--complete_003_6_GDD_FULL_more_E022-11.gex
      - Yes
      - Yes
    * - 93
      - examples--complete2--006--complete_010_Other_Auxiliary_aux2_e04f.gex
      - Yes
      - Yes
    * - 94
      - examples--complete2--006--complete_004_6_GDD_FULL_81-109_98.gex
      - Yes
      - Yes
    * - 95
      - examples--complete2--006--complete_001_6_GDD_FULL_61-80_72.gex
      - Yes
      - Yes
    * - 96
      - examples--complete2--006--complete_013_7_Book_00EE_11_E075-26.gex
      - Yes
      - Yes
    * - 97
      - examples--complete2--006--complete_015_7_Book_00EE_06_E057-38.gex
      - Yes
      - Yes
    * - 98
      - examples--complete2--006--complete_014_7_Book_00EE_07_E059-47.gex
      - Yes
      - Yes
    * - 99
      - examples--complete2--006--complete_014_7_Book_00EE_07_E059-53.gex
      - Yes
      - Yes
    * - 100
      - examples--complete2--006--complete_003_6_GDD_FULL_more_E023-15.gex
      - Yes
      - Yes
    * - 101
      - examples--complete2--011--complete_002_6_GDD_FULL_01-20_12.gex
      - Yes
      - Yes
    * - 102
      - examples--complete2--011--complete_002_6_GDD_FULL_01-20_05.gex
      - Yes
      - Yes
    * - 103
      - examples--complete2--011--complete_003_6_GDD_FULL_21-40_34.gex
      - Yes
      - Yes
    * - 104
      - examples--complete2--011--complete_004_6_GDD_FULL_81-109_99.gex
      - Yes
      - Yes
    * - 105
      - examples--complete2--011--complete_003_6_GDD_FULL_21-40_35.gex
      - Yes
      - Yes
    * - 106
      - examples--complete2--011--complete_003_6_GDD_FULL_21-40_31.gex
      - Yes
      - Yes
    * - 107
      - examples--complete2--011--complete_002_6_GDD_FULL_41-60_41.gex
      - 
      - Yes
    * - 108
      - examples--complete2--011--complete_002_6_GDD_FULL_41-60_43.gex
      - Yes
      - Yes
    * - 109
      - examples--complete2--011--complete_002_6_GDD_FULL_41-60_51.gex
      - Yes
      - Yes
    * - 110
      - examples--complete2--011--complete_002_6_GDD_FULL_41-60_44.gex
      - Yes
      - Yes
    * - 111
      - examples--complete2--010--complete_004_6_GDD_FULL_21-40_29.gex
      - Yes
      - Yes
    * - 112
      - examples--complete2--010--complete_002_6_GDD_FULL_01-20_10.gex
      - Yes
      - Yes
    * - 113
      - examples--complete2--010--complete_013_7_Book_00EE_10_E072-15.gex
      - Yes
      - Yes
    * - 114
      - examples--complete2--010--complete_011_7_Book_00EE_04_E051-6.gex
      - Yes
      - Yes
    * - 115
      - examples--complete2--010--complete_012_7_Book_00EE_05_E051-20.gex
      - Yes
      - Yes
    * - 116
      - examples--complete2--010--complete_011_7_Book_00EE_03_E037-20.gex
      - Yes
      - Yes
    * - 117
      - examples--complete2--010--complete_012_7_Book_00EE_11_E076-32.gex
      - Yes
      - Yes
    * - 118
      - examples--complete2--010--complete_000_3_JAR_JAR02-new_fig214.gex
      - Yes
      - Yes
    * - 119
      - examples--complete2--010--complete_003_6_GDD_FULL_more_E021-3.gex
      - Yes
      - Yes
    * - 120
      - examples--complete2--010--complete_013_7_Book_00EE_10_E074-22.gex
      - Yes
      - Yes
    * - 121
      - examples--complete2--010--complete_001_6_GDD_FULL_01-20_20.gex
      - Yes
      - Yes
    * - 122
      - examples--complete2--010--complete_002_6_GDD_FULL_41-60_57.gex
      - Yes
      - Yes
    * - 123
      - examples--complete2--010--complete_010_Other_Auxiliary_ye_aux_ppara.gex
      - Yes
      - Yes
    * - 124
      - examples--complete2--003--complete_003_6_GDD_FULL_more_E013-3.gex
      - Yes
      - Yes
    * - 125
      - examples--complete2--003--complete_005_Other_ndgs_01.gex
      - Yes
      - Yes
    * - 126
      - examples--complete2--003--complete_013_7_Book_00EE_10_E072-12.gex
      - Yes
      - Yes
    * - 127
      - examples--complete2--003--complete_010_Other_Auxiliary_ye_aux_wang3.gex
      - Yes
      - Yes
    * - 128
      - examples--complete2--003--complete_003_6_GDD_FULL_more_E022-8.gex
      - Yes
      - Yes
    * - 129
      - examples--complete2--003--complete_008_ex-gao_ex160_206.gex
      - Yes
      - Yes
    * - 130
      - examples--complete2--003--complete_013_7_Book_00EE_11_E077-38.gex
      - Yes
      - Yes
    * - 131
      - examples--complete2--003--complete_004_6_GDD_FULL_81-109_84.gex
      - Yes
      - Yes
    * - 132
      - examples--complete2--003--complete_003_6_GDD_FULL_more_E022-10.gex
      - Yes
      - Yes
    * - 133
      - examples--complete2--003--complete_011_7_Book_00EE_03_E037-25.gex
      - Yes
      - Yes
    * - 134
      - examples--complete2--003--complete_016_7_Book_00EE_06_E051-25.gex
      - Yes
      - Yes
    * - 135
      - examples--complete2--003--complete_013_7_Book_00EE_10_E074-20.gex
      - Yes
      - Yes
    * - 136
      - examples--complete2--003--complete_017_ex-gao_ex160_4_003.gex
      - Yes
      - Yes
    * - 137
      - examples--complete2--003--complete_015_7_Book_00EE_08_E059-56.gex
      - Yes
      - Yes
    * - 138
      - examples--complete2--003--complete_014_7_Book_00EE_07_E059-52.gex
      - Yes
      - Yes
    * - 139
      - examples--complete2--004--complete_002_6_GDD_FULL_01-20_13.gex
      - Yes
      - Yes
    * - 140
      - examples--complete2--004--complete_006_Other_Auxiliary_E092-5.gex
      - 
      - 
    * - 141
      - examples--complete2--004--complete_004_6_GDD_FULL_81-109_86.gex
      - Yes
      - Yes
    * - 142
      - examples--complete2--004--complete_011_7_Book_00EE_03_E037-26.gex
      - Yes
      - Yes
    * - 143
      - examples--complete2--004--complete_016_7_Book_00EE_06_E051-27.gex
      - Yes
      - Yes
    * - 144
      - examples--complete2--004--complete_001_6_GDD_FULL_61-80_73.gex
      - Yes
      - Yes
    * - 145
      - examples--complete2--004--complete_014_7_Book_00EE_07_E057-42.gex
      - Yes
      - Yes
    * - 146
      - examples--complete2--005--complete_005_Other_ndgs_03.gex
      - Yes
      - Yes
    * - 147
      - examples--complete2--005--complete_000_rebuilt example_9point.gex
      - Yes
      - Yes
    * - 148
      - examples--complete2--005--complete_013_7_Book_00EE_11_E081-2.gex
      - Yes
      - Yes
    * - 149
      - examples--complete2--005--complete_002_6_GDD_FULL_41-60_58.gex
      - Yes
      - Yes
    * - 150
      - examples--complete2--005--complete_016_7_Book_00EE_06_E051-26.gex
      - Yes
      - Yes
    * - 151
      - examples--complete2--005--complete_001_6_GDD_FULL_61-80_61.gex
      - Yes
      - Yes
    * - 152
      - examples--complete2--005--complete_017_ex-gao_ex160_4_e03a_lratio.gex
      - Yes
      - Yes
    * - 153
      - examples--complete2--005--complete_008_ex-gao_ex160_e122.gex
      - Yes
      - Yes
    * - 154
      - examples--complete2--002--complete_007_7_Book_LLL_yL251-1.gex
      - Yes
      - Yes
    * - 155
      - examples--complete2--002--complete_017_ex-gao_ex160_4_e12.gex
      - Yes
      - Yes
    * - 156
      - examples--complete2--002--complete_013_7_Book_00EE_10_E073-18.gex
      - Yes
      - Yes
    * - 157
      - examples--complete2--002--complete_011_7_Book_00EE_03_E043-3.gex
      - Yes
      - Yes
    * - 158
      - examples--complete2--002--complete_012_7_Book_00EE_02_E028-2-1.gex
      - Yes
      - Yes
    * - 159
      - examples--complete2--002--complete_008_ex-gao_ex160_e124.gex
      - Yes
      - Yes
    * - 160
      - examples--complete2--000--complete_004_6_GDD_FULL_81-109_106.gex
      - Yes
      - Yes
    * - 161
      - examples--complete2--unsolved2--complete_010_Other_Auxiliary_ye_aux_think2.gex
      - 
      - 
    * - 162
      - examples--complete2--unsolved2--complete_012_7_Book_00EE_02_E023-21.gex
      - Yes
      - Yes
    * - 163
      - examples--complete2--unsolved2--complete_006_7_Book_LLL_yL252-6.gex
      - Yes
      - Yes
    * - 164
      - examples--complete2--unsolved2--complete_015_7_Book_00EE_08_E059-59.gex
      - 
      - 
    * - 165
      - examples--complete2--unsolved2--complete_013_7_Book_00EE_10_E072-16.gex
      - 
      - 
    * - 166
      - examples--complete2--unsolved2--complete_003_6_GDD_FULL_more_E023-19.gex
      - Yes
      - Yes
    * - 167
      - examples--complete2--unsolved2--complete_010_Other_Auxiliary_ye_aux_ll43.gex
      - 
      - 
    * - 168
      - examples--complete2--unsolved2--complete_010_Other_Auxiliary_aux2_22.gex
      - 
      - 
    * - 169
      - examples--complete2--unsolved2--complete_014_7_Book_00EE_09_E066-04.gex
      - Yes
      - Yes
    * - 170
      - examples--complete2--unsolved2--complete_014_7_Book_00EE_08_E061-66.gex
      - Yes
      - Yes
    * - 171
      - examples--complete2--unsolved2--complete_011_7_Book_00EE_03_E037-24.gex
      - Yes
      - Yes
    * - 172
      - examples--complete2--unsolved2--complete_014_7_Book_00EE_08_E061-65.gex
      - Yes
      - Yes
    * - 173
      - examples--complete2--unsolved2--complete_012_7_Book_00EE_11_E076-31.gex
      - 
      - 
    * - 174
      - examples--complete2--unsolved2--complete_010_Other_Auxiliary_ye_aux_y1.gex
      - 
      - 
    * - 175
      - examples--complete2--unsolved2--complete_004_6_GDD_FULL_21-40_40.gex
      - Yes
      - Yes
    * - 176
      - examples--complete2--unsolved2--complete_014_7_Book_00EE_09_E069-8.gex
      - 
      - 
    * - 177
      - examples--complete2--unsolved2--complete_011_7_Book_00EE_04_E051-9.gex
      - 
      - 
    * - 178
      - examples--complete2--unsolved2--complete_003_6_GDD_FULL_21-40_27.gex
      - Yes
      - Yes
    * - 179
      - examples--complete2--unsolved2--complete_017_ex-gao_ex160_4_e08.gex
      - Yes
      - Yes
    * - 180
      - examples--complete2--unsolved2--complete_015_7_Book_00EE_06_E051-29.gex
      - Yes
      - Yes
    * - 181
      - examples--complete2--unsolved2--complete_002_6_GDD_FULL_41-60_42.gex
      - 
      - 
    * - 182
      - examples--complete2--unsolved2--complete_014_7_Book_00EE_08_E061-63f.gex
      - Yes
      - Yes
    * - 183
      - examples--complete2--unsolved2--complete_007_7_Book_LLL_yL198-1.gex
      - 
      - 
    * - 184
      - examples--complete2--unsolved--complete_015_7_Book_00EE_08_E061-61.gex
      - 
      - 
    * - 185
      - examples--complete2--unsolved--complete_008_ex-gao_ex160_204.gex
      - Yes
      - Yes
    * - 186
      - examples--complete2--unsolved--complete_005_Other_unsolved_65.gex
      - Yes
      - Yes
    * - 187
      - examples--complete2--unsolved--complete_008_ex-gao_ex160_005.gex
      - 
      - 
    * - 188
      - examples--complete2--unsolved--complete_006_Other_ndgTest_65.gex
      - Yes
      - Yes
    * - 189
      - examples--complete2--unsolved--complete_005_Other_unsolved_E051-7.gex
      - Yes
      - Yes
    * - 190
      - examples--complete2--unsolved--complete_005_Other_unsolved_E046-10.gex
      - Yes
      - Yes
    * - 191
      - examples--complete2--unsolved--ex-gao_ex160_103.gex
      - Yes
      - Yes
    * - 192
      - examples--complete2--unsolved--ex-gao_ex160_104.gex
      - Yes
      - Yes
    * - 193
      - examples--complete2--unsolved--complete_005_Other_unsolved_109f.gex
      - 
      - 
    * - 194
      - examples--complete2--unsolved--complete_005_Other_unsolved_E046-7.gex
      - Yes
      - Yes
    * - 195
      - examples--complete2--unsolved--complete_008_ex-gao_ex160_e121.gex
      - Yes
      - Yes
    * - 196
      - examples--complete2--unsolved--complete_018_ex-gao_ex160_4_010.gex
      - Yes
      - Yes
    * - 197
      - examples--complete2--unsolved--complete_005_Other_unsolved_82.gex
      - 
      - Yes
    * - 198
      - examples--complete2--unsolved--complete_014_7_Book_00EE_07_E057-41.gex
      - 
      - 
    * - 199
      - examples--complete2--unsolved--complete_015_7_Book_00EE_08_E059-55.gex
      - Yes
      - Yes
    * - 200
      - examples--complete2--unsolved--complete_005_Other_unsolved_E073-17.gex
      - Yes
      - Yes
    * - 201
      - examples--complete2--unsolved--complete_015_7_Book_00EE_06_E056-33.gex
      - Yes
      - Yes
    * - 202
      - examples--complete2--unsolved--complete_005_Other_unsolved_E074-24.gex
      - Yes
      - Yes
    * - 203
      - examples--complete2--unsolved1--complete_008_7_Book_LLL_L057-3.gex
      - Yes
      - Yes
    * - 204
      - examples--complete2--unsolved1--complete_006_7_Book_LLL_L046-17.gex
      - Yes
      - Yes
    * - 205
      - examples--complete2--unsolved1--complete_008_7_Book_LLL_L057-2.gex
      - Yes
      - Yes
    * - 206
      - examples--complete2--unsolved1--complete_008_ex-gao_ex160_e102.gex
      - 
      - 
    * - 207
      - examples--complete2--unsolved1--complete_012_7_Book_00EE_11_E075-27f.gex
      - 
      - 
    * - 208
      - examples--complete2--unsolved1--complete_006_7_Book_LLL_L091-13.gex
      - 
      - 
    * - 209
      - examples--complete2--unsolved1--complete_010_Other_gao_Y_yL157-1.gex
      - 
      - 
    * - 210
      - examples--complete2--unsolved1--complete_008_7_Book_LLL_L055-5.gex
      - 
      - Yes
    * - 211
      - examples--complete2--unsolved1--complete_013_7_Book_00EE_11_E075-29.gex
      - Yes
      - Yes
    * - 212
      - examples--complete2--unsolved1--complete_012_7_Book_00EE_05_E051-14-1.gex
      - 
      - 
    * - 213
      - examples--complete2--unsolved1--complete_007_7_Book_LLL_L057-3-1.gex
      - Yes
      - Yes
    * - 214
      - examples--complete2--unsolved1--complete_001_6_GDD_FULL_61-80_80.gex
      - Yes
      - Yes
    * - 215
      - examples--complete2--unsolved1--complete_008_ex-gao_ex160_e213.gex
      - Yes
      - Yes
    * - 216
      - examples--complete2--unsolved1--complete_011_7_Book_00EE_04_E051-2.gex
      - 
      - 
    * - 217
      - examples--complete2--unsolved1--complete_007_7_Book_LLL_L043-5.gex
      - Yes
      - Yes
    * - 218
      - examples--complete2--unsolved1--complete_001_6_GDD_FULL_61-80_71.gex
      - Yes
      - Yes
    * - 219
      - examples--complete2--unsolved1--complete_007_7_Book_LLL_L043-5-1.gex
      - Yes
      - Yes
    * - 220
      - examples--complete2--unsolved1--complete_011_7_Book_00EE_04_E051-8.gex
      - Yes
      - Yes
    * - 221
      - examples--complete2--unsolved1--complete_013_7_Book_00EE_10_E072-8.gex
      - Yes
      - Yes
    * - 222
      - examples--complete2--unsolved1--complete_003_6_GDD_FULL_more_E023-14.gex
      - Yes
      - Yes
    * - 223
      - examples--complete2--unsolved1--complete_010_Other_gao_Y_yL182-1.gex
      - 
      - 
    * - 224
      - examples--complete2--unsolved1--complete_008_ex-gao_ex160_e120.gex
      - Yes
      - Yes
    * - 225
      - new_unsolved--0.gex
      - 
      - 
    * - 226
      - new_unsolved--1.gex
      - 
      - 
    * - 227
      - examples--complete2--unsolved1--complete_009_Other_paper_Thebault_t5.gex
      - 
      - 
    * - 228
      - examples--complete2--unsolved--complete_013_7_Book_00EE_10_E072-11.gex
      - Yes
      - Yes
    * - 229
      - examples--complete2--unsolved2--complete_015_7_Book_00EE_06_E051-28.gex
      - Yes
      - Yes
    * - 230
      - examples--complete2--unsolved2--complete_010_Other_Auxiliary_ye_aux_think.gex
      - 
      - 
    * - 231
      - examples--complete2--unsolved--morley.gex
      - 
      - 
    * - 
      - Total numbers
      - 198
      - 201