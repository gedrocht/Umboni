!> Entry point for the New England weather simulation executable.
program main
  use command_line_argument_parser, only: parse_command_line_options, simulation_command_line_options
  use forecast_consensus_engine, only: build_location_forecasts
  use json_forecast_writer, only: write_forecast_json
  use normalized_weather_csv_reader, only: read_normalized_weather_csv
  use structured_logging, only: append_log_entry
  use weather_data_types, only: location_forecast_bundle, provider_hourly_forecast_record
  implicit none

  type(simulation_command_line_options) :: command_line_options
  type(provider_hourly_forecast_record), allocatable :: provider_records(:)
  type(location_forecast_bundle), allocatable :: location_forecasts(:)
  character(len=1024) :: python_fetch_command
  integer :: fetch_exit_status

  command_line_options = parse_command_line_options()

  call append_log_entry(command_line_options%log_file_path, 'INFO', 'The Fortran simulator is starting.')

  if (.not. command_line_options%skip_fetch) then
    python_fetch_command = trim(command_line_options%python_command) // &
      ' "scripts/run_weather_fetcher.py" --output-csv "' // trim(command_line_options%input_csv_path) // &
      '" --log-file "artifacts/logs/python-fetcher.log.jsonl"'

    call append_log_entry(command_line_options%log_file_path, 'INFO', &
      'The simulator is invoking the Python fetch layer.')

    call execute_command_line(trim(python_fetch_command), wait=.true., exitstat=fetch_exit_status)
    if (fetch_exit_status /= 0) then
      call append_log_entry(command_line_options%log_file_path, 'ERROR', &
        'The Python fetch layer returned a non-zero exit code.')
      stop 'Python fetch layer failed.'
    end if
  end if

  call read_normalized_weather_csv(command_line_options%input_csv_path, provider_records)
  call append_log_entry(command_line_options%log_file_path, 'INFO', &
    'Normalized provider records were read successfully.')

  call build_location_forecasts(provider_records, location_forecasts)
  call append_log_entry(command_line_options%log_file_path, 'INFO', &
    'Regional location forecasts were generated successfully.')

  call write_forecast_json(command_line_options%output_json_path, location_forecasts)
  call append_log_entry(command_line_options%log_file_path, 'INFO', &
    'The JSON forecast artifact was written successfully.')
end program main
