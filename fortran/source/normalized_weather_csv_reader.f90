!> Reads the normalized provider output written by the Python fetcher.
module normalized_weather_csv_reader
  use, intrinsic :: iso_fortran_env, only: real64
  use string_utilities, only: parse_integer_value, parse_real_value, split_comma_separated_line
  use weather_data_types, only: missing_numeric_value, provider_hourly_forecast_record, text_field_length
  implicit none
  private

  public :: read_normalized_weather_csv

contains

  !> Loads every provider record from a normalized comma-separated-values file.
  subroutine read_normalized_weather_csv(input_file_path, provider_records)
    character(len=*), intent(in) :: input_file_path
    type(provider_hourly_forecast_record), allocatable, intent(out) :: provider_records(:)

    character(len=1024) :: input_line
    integer :: input_unit
    integer :: read_status
    integer :: record_count
    integer :: current_record_index

    record_count = count_data_rows(input_file_path)
    allocate(provider_records(record_count))

    open(newunit=input_unit, file=trim(input_file_path), status='old', action='read', iostat=read_status)
    if (read_status /= 0) then
      stop 'Unable to open normalized weather CSV input.'
    end if

    read(input_unit, '(A)', iostat=read_status) input_line

    current_record_index = 0
    do
      read(input_unit, '(A)', iostat=read_status) input_line
      if (read_status /= 0) then
        exit
      end if

      if (len_trim(input_line) == 0) then
        cycle
      end if

      current_record_index = current_record_index + 1
      provider_records(current_record_index) = parse_record_from_line(input_line)
    end do

    close(input_unit)
  end subroutine read_normalized_weather_csv

  !> Counts how many data rows exist so the output array can be allocated exactly once.
  integer function count_data_rows(input_file_path)
    character(len=*), intent(in) :: input_file_path

    character(len=1024) :: input_line
    integer :: input_unit
    integer :: read_status

    count_data_rows = 0

    open(newunit=input_unit, file=trim(input_file_path), status='old', action='read', iostat=read_status)
    if (read_status /= 0) then
      stop 'Unable to count rows in normalized weather CSV input.'
    end if

    read(input_unit, '(A)', iostat=read_status) input_line

    do
      read(input_unit, '(A)', iostat=read_status) input_line
      if (read_status /= 0) then
        exit
      end if

      if (len_trim(input_line) > 0) then
        count_data_rows = count_data_rows + 1
      end if
    end do

    close(input_unit)
  end function count_data_rows

  !> Parses one line into the derived type used throughout the engine.
  function parse_record_from_line(input_line) result(parsed_record)
    character(len=*), intent(in) :: input_line
    type(provider_hourly_forecast_record) :: parsed_record

    character(len=text_field_length) :: split_fields(14)

    call split_comma_separated_line(input_line, split_fields)

    parsed_record%provider_name = split_fields(1)
    parsed_record%state_name = split_fields(2)
    parsed_record%location_name = split_fields(3)
    parsed_record%latitude_degrees = parse_real_value(split_fields(4), 0.0_real64)
    parsed_record%longitude_degrees = parse_real_value(split_fields(5), 0.0_real64)
    parsed_record%altitude_meters = parse_real_value(split_fields(6), 0.0_real64)
    parsed_record%forecast_hour_offset = parse_integer_value(split_fields(7), 0)
    parsed_record%forecast_timestamp_utc = split_fields(8)
    parsed_record%air_temperature_celsius = parse_real_value(split_fields(9), missing_numeric_value)
    parsed_record%relative_humidity_percentage = parse_real_value(split_fields(10), missing_numeric_value)
    parsed_record%wind_speed_kilometers_per_hour = parse_real_value(split_fields(11), missing_numeric_value)
    parsed_record%precipitation_probability_percentage = parse_real_value(split_fields(12), missing_numeric_value)
    parsed_record%surface_pressure_hectopascals = parse_real_value(split_fields(13), missing_numeric_value)
    parsed_record%cloud_cover_percentage = parse_real_value(split_fields(14), missing_numeric_value)
  end function parse_record_from_line

end module normalized_weather_csv_reader

