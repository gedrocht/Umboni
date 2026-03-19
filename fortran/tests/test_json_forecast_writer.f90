program test_json_forecast_writer
  use json_forecast_writer, only: write_forecast_json
  use test_support, only: assert_true, finish_tests
  use weather_data_types, only: location_forecast_bundle, simulated_hour_count
  implicit none

  type(location_forecast_bundle) :: location_forecasts(1)
  character(len=256) :: json_line
  integer :: input_output_status
  integer :: output_unit
  logical :: found_region_name
  logical :: found_location_name

  location_forecasts(1)%state_name = 'Massachusetts'
  location_forecasts(1)%location_name = 'Boston'
  location_forecasts(1)%latitude_degrees = 42.3601
  location_forecasts(1)%longitude_degrees = -71.0589
  allocate(location_forecasts(1)%hourly_forecasts(simulated_hour_count))
  location_forecasts(1)%hourly_forecasts(1)%forecast_hour_offset = 1
  location_forecasts(1)%hourly_forecasts(1)%forecast_timestamp_utc = '2026-03-18T13:00:00Z'
  location_forecasts(1)%hourly_forecasts(1)%ensemble_air_temperature_celsius = 10.5
  location_forecasts(1)%hourly_forecasts(1)%confidence_percentage = 100.0

  call write_forecast_json('artifacts/generated/fortran-json-writer-test.json', location_forecasts)

  found_region_name = .false.
  found_location_name = .false.

  open(newunit=output_unit, file='artifacts/generated/fortran-json-writer-test.json', status='old', &
    action='read', iostat=input_output_status)
  if (input_output_status /= 0) then
    call assert_true(.false., 'The JSON writer test output file should exist.')
    call finish_tests()
  end if

  do
    read(output_unit, '(A)', iostat=input_output_status) json_line
    if (input_output_status /= 0) then
      exit
    end if

    if (index(json_line, '"regionName"') > 0) then
      found_region_name = .true.
    end if

    if (index(json_line, '"locationName": "Boston"') > 0) then
      found_location_name = .true.
    end if
  end do

  close(output_unit)

  call assert_true(found_region_name, 'The JSON output should include the regionName property.')
  call assert_true(found_location_name, 'The JSON output should include the Boston location name.')
  call finish_tests()
end program test_json_forecast_writer
