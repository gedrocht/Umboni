program test_forecast_consensus_engine
  use, intrinsic :: iso_fortran_env, only: real64
  use forecast_consensus_engine, only: build_location_forecasts
  use test_support, only: assert_almost_equal_real, assert_equal_integer, assert_equal_string, finish_tests
  use weather_data_types, only: location_forecast_bundle, provider_hourly_forecast_record
  implicit none

  type(provider_hourly_forecast_record) :: provider_records(4)
  type(location_forecast_bundle), allocatable :: location_forecasts(:)

  provider_records(1)%provider_name = 'Open-Meteo'
  provider_records(1)%state_name = 'Massachusetts'
  provider_records(1)%location_name = 'Boston'
  provider_records(1)%forecast_hour_offset = 1
  provider_records(1)%forecast_timestamp_utc = '2026-03-18T13:00:00Z'
  provider_records(1)%air_temperature_celsius = 10.0_real64
  provider_records(1)%wind_speed_kilometers_per_hour = 15.0_real64

  provider_records(2)%provider_name = 'National Weather Service'
  provider_records(2)%state_name = 'Massachusetts'
  provider_records(2)%location_name = 'Boston'
  provider_records(2)%forecast_hour_offset = 1
  provider_records(2)%forecast_timestamp_utc = '2026-03-18T13:00:00Z'
  provider_records(2)%air_temperature_celsius = 12.0_real64
  provider_records(2)%wind_speed_kilometers_per_hour = 12.0_real64

  provider_records(3)%provider_name = 'MET Norway'
  provider_records(3)%state_name = 'Massachusetts'
  provider_records(3)%location_name = 'Boston'
  provider_records(3)%forecast_hour_offset = 1
  provider_records(3)%forecast_timestamp_utc = '2026-03-18T13:00:00Z'
  provider_records(3)%air_temperature_celsius = 11.0_real64
  provider_records(3)%wind_speed_kilometers_per_hour = 9.0_real64

  provider_records(4)%provider_name = '7Timer'
  provider_records(4)%state_name = 'Massachusetts'
  provider_records(4)%location_name = 'Boston'
  provider_records(4)%forecast_hour_offset = 1
  provider_records(4)%forecast_timestamp_utc = '2026-03-18T13:00:00Z'
  provider_records(4)%air_temperature_celsius = 9.0_real64
  provider_records(4)%wind_speed_kilometers_per_hour = 18.0_real64

  allocate(location_forecasts(0))
  call build_location_forecasts(provider_records, location_forecasts)

  call assert_equal_integer(1, size(location_forecasts), 'Exactly one location forecast should be created.')
  call assert_equal_string('Boston', location_forecasts(1)%location_name, 'The location name should survive aggregation.')
  call assert_equal_integer(4, location_forecasts(1)%hourly_forecasts(1)%provider_coverage_count, &
    'All four providers should contribute to the first hour.')
  call assert_almost_equal_real(10.70_real64, location_forecasts(1)%hourly_forecasts(1)%ensemble_air_temperature_celsius, &
    0.01_real64, 'The weighted temperature average should match the configured provider weights.')
  call assert_almost_equal_real(13.05_real64, location_forecasts(1)%hourly_forecasts(1)%ensemble_wind_speed_kilometers_per_hour, &
    0.01_real64, 'The weighted wind-speed average should match the configured provider weights.')

  call finish_tests()
end program test_forecast_consensus_engine
