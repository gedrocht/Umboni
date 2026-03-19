program test_normalized_weather_csv_reader
  use normalized_weather_csv_reader, only: read_normalized_weather_csv
  use test_support, only: assert_equal_integer, assert_equal_string, finish_tests
  use weather_data_types, only: provider_hourly_forecast_record
  implicit none

  type(provider_hourly_forecast_record), allocatable :: provider_records(:)

  call read_normalized_weather_csv('samples/normalized-provider-observations.csv', provider_records)

  call assert_equal_integer(4, size(provider_records), 'The sample fixture should contain four provider rows.')
  call assert_equal_string('Open-Meteo', provider_records(1)%provider_name, 'The first provider should be Open-Meteo.')
  call assert_equal_string('Boston', provider_records(1)%location_name, 'The first location should be Boston.')
  call assert_equal_integer(2, provider_records(4)%forecast_hour_offset, 'The final fixture row should represent hour two.')

  call finish_tests()
end program test_normalized_weather_csv_reader
