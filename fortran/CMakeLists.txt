add_library(
  weather_simulation_engine
  source/weather_data_types.f90
  source/string_utilities.f90
  source/time_formatting_utilities.f90
  source/structured_logging.f90
  source/provider_weight_catalog.f90
  source/normalized_weather_csv_reader.f90
  source/forecast_consensus_engine.f90
  source/json_forecast_writer.f90
  source/command_line_argument_parser.f90
)

target_include_directories(
  weather_simulation_engine
  PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/source
)

add_executable(
  new_england_weather_simulator
  source/main.f90
)

target_link_libraries(
  new_england_weather_simulator
  PRIVATE
    weather_simulation_engine
)

if(BUILD_TESTING)
  add_library(
    weather_test_support
    tests/test_support.f90
  )

  target_link_libraries(
    weather_test_support
    PUBLIC
      weather_simulation_engine
  )

  add_executable(
    forecast_consensus_engine_test
    tests/test_forecast_consensus_engine.f90
  )

  target_link_libraries(
    forecast_consensus_engine_test
    PRIVATE
      weather_test_support
  )

  add_test(
    NAME forecast_consensus_engine_test
    COMMAND forecast_consensus_engine_test
  )
  set_tests_properties(forecast_consensus_engine_test PROPERTIES WORKING_DIRECTORY ${PROJECT_SOURCE_DIR})

  add_executable(
    normalized_weather_csv_reader_test
    tests/test_normalized_weather_csv_reader.f90
  )

  target_link_libraries(
    normalized_weather_csv_reader_test
    PRIVATE
      weather_test_support
  )

  add_test(
    NAME normalized_weather_csv_reader_test
    COMMAND normalized_weather_csv_reader_test
  )
  set_tests_properties(normalized_weather_csv_reader_test PROPERTIES WORKING_DIRECTORY ${PROJECT_SOURCE_DIR})

  add_executable(
    json_forecast_writer_test
    tests/test_json_forecast_writer.f90
  )

  target_link_libraries(
    json_forecast_writer_test
    PRIVATE
      weather_test_support
  )

  add_test(
    NAME json_forecast_writer_test
    COMMAND json_forecast_writer_test
  )
  set_tests_properties(json_forecast_writer_test PROPERTIES WORKING_DIRECTORY ${PROJECT_SOURCE_DIR})
endif()
