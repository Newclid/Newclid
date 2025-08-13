foreach(name
    add_circle
    #angle
    #dist
    #equation
    linear_combination
    #linear_system -- disabled for now b/c of API change
    #sin_or_dist -- disabled for now b/c of API change
    #point
    #problem
    #reduced_equation -- disabled for now b/c of API change
    rat_sqrt
    root_rat
    int_sqrt
    #slope_angle
    #squared_dist
  )
  add_executable(test_${name} ${name}.cpp)

  target_link_libraries(test_${name} PRIVATE
    yuclid
    Boost::unit_test_framework)

  add_test(NAME ${name} COMMAND test_${name})

endforeach(name)

foreach(name
    2000_p1
    2002_p2a
    2002_p2b
    2003_p4
    2004_p1
    2004_p5
    2005_p5
    2007_p4
    2010_p4
    2012_p1
    2013_p4
    2014_p4
    2015_p4
    2016_p1
    2017_p4
    2019_p2_easy
    2022_p4
  )
  add_test(NAME "solve IMO ${name}"
    COMMAND yuclid_exe --err-on-failure --mode ddar --log-level debug
    --disable-ar-sin
    --input-file "${CMAKE_CURRENT_SOURCE_DIR}/imo_ag_30/translated_imo_${name}.txt")
endforeach(name)

foreach(name
    2000_p6
    2008_p1a
    2008_p1b
    2008_p6
    2009_p2
    2010_p2
    2011_p6
    2012_p5
    2015_p3
    2018_p1
    2019_p2
    2019_p6
    2020_p1
    2021_p3
  )
  add_test(NAME "solve IMO ${name} (xfail)"
    COMMAND yuclid_exe --err-on-failure --mode ddar
    --disable-ar-sin
    --input-file "${CMAKE_CURRENT_SOURCE_DIR}/imo_ag_30/translated_imo_${name}.txt")
  set_tests_properties("solve IMO ${name} (xfail)" PROPERTIES WILL_FAIL TRUE)
endforeach(name)


file(GLOB ratio_only_tests RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} ratio_only/*.txt)
foreach(name ${ratio_only_tests})
  add_test(NAME "solve ${name} with ratio only"
    COMMAND yuclid_exe --disable-ar-dist --disable-ar-squared
    --disable-eqn-statements --err-on-failure --log-level debug
    --mode ddar --input-file "${CMAKE_CURRENT_SOURCE_DIR}/${name}")
endforeach(name)

set_tests_properties("solve ratio_only/r44_pappus_theorem.txt with ratio only"
  PROPERTIES WILL_FAIL TRUE)
set_tests_properties("solve ratio_only/r70_projective_harmonic_conjugate.txt with ratio only"
  PROPERTIES WILL_FAIL TRUE)

file(GLOB no_crash_tests RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} no_crash/*.txt)
foreach(name ${no_crash_tests})
  add_test(NAME "Check that ${name} doesn't crash with ratio only"
    COMMAND yuclid_exe --disable-ar-dist --disable-ar-squared
    --disable-eqn-statements
    --mode ddar --input-file "${CMAKE_CURRENT_SOURCE_DIR}/${name}")
endforeach(name)
