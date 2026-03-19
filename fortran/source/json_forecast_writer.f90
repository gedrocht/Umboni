!> Writes the public forecast bundles to a JSON file that the Angular frontend can consume.
module json_forecast_writer
  use, intrinsic :: iso_fortran_env, only: real64
  use weather_data_types, only: location_forecast_bundle, missing_numeric_value
  implicit none
  private

  public :: write_forecast_json

contains

  !> Writes a complete JSON document with one array entry per location.
  subroutine write_forecast_json(output_file_path, location_forecasts)
    character(len=*), intent(in) :: output_file_path
    type(location_forecast_bundle), intent(in) :: location_forecasts(:)

    integer :: output_unit
    integer :: open_status
    integer :: current_location_index

    open(newunit=output_unit, file=trim(output_file_path), status='replace', action='write', iostat=open_status)
    if (open_status /= 0) then
      stop 'Unable to open JSON forecast output file.'
    end if

    write(output_unit, '(A)') '{'
    write(output_unit, '(A)') '  "regionName": "New England",'
    write(output_unit, '(A,I0,A)') '  "locationCount": ', size(location_forecasts), ','
    write(output_unit, '(A)') '  "locations": ['

    do current_location_index = 1, size(location_forecasts)
      call write_location_json(output_unit, location_forecasts(current_location_index), &
        current_location_index == size(location_forecasts))
    end do

    write(output_unit, '(A)') '  ]'
    write(output_unit, '(A)') '}'

    close(output_unit)
  end subroutine write_forecast_json

  !> Writes one location block including all 24 hourly forecasts and a simple daily summary.
  subroutine write_location_json(output_unit, location_forecast, is_final_location)
    integer, intent(in) :: output_unit
    type(location_forecast_bundle), intent(in) :: location_forecast
    logical, intent(in) :: is_final_location

    integer :: current_hour_index
    real(real64) :: minimum_temperature_celsius
    real(real64) :: maximum_temperature_celsius

    call summarize_temperature_range(location_forecast, minimum_temperature_celsius, maximum_temperature_celsius)

    write(output_unit, '(A)') '    {'
    write(output_unit, '(A,A,A)') '      "stateName": "', trim(location_forecast%state_name), '",'
    write(output_unit, '(A,A,A)') '      "locationName": "', trim(location_forecast%location_name), '",'
    write(output_unit, '(A,F0.4,A)') '      "latitudeDegrees": ', location_forecast%latitude_degrees, ','
    write(output_unit, '(A,F0.4,A)') '      "longitudeDegrees": ', location_forecast%longitude_degrees, ','
    write(output_unit, '(A)') '      "dailySummary": {'
    write(output_unit, '(A,F0.2,A)') '        "minimumTemperatureCelsius": ', minimum_temperature_celsius, ','
    write(output_unit, '(A,F0.2)') '        "maximumTemperatureCelsius": ', maximum_temperature_celsius
    write(output_unit, '(A)') '      },'
    write(output_unit, '(A)') '      "hourlyForecasts": ['

    do current_hour_index = 1, size(location_forecast%hourly_forecasts)
      call write_hourly_forecast_json(output_unit, location_forecast%hourly_forecasts(current_hour_index), &
        current_hour_index == size(location_forecast%hourly_forecasts))
    end do

    write(output_unit, '(A)') '      ]'
    if (is_final_location) then
      write(output_unit, '(A)') '    }'
    else
      write(output_unit, '(A)') '    },'
    end if
  end subroutine write_location_json

  !> Writes one hourly forecast object.
  subroutine write_hourly_forecast_json(output_unit, hourly_forecast, is_final_hour)
    use weather_data_types, only: hourly_regional_forecast

    integer, intent(in) :: output_unit
    type(hourly_regional_forecast), intent(in) :: hourly_forecast
    logical, intent(in) :: is_final_hour

    write(output_unit, '(A)') '        {'
    write(output_unit, '(A,I0,A)') '          "forecastHourOffset": ', hourly_forecast%forecast_hour_offset, ','
    write(output_unit, '(A,A,A)') '          "forecastTimestampUtc": "', trim(hourly_forecast%forecast_timestamp_utc), '",'
    write(output_unit, '(A,F0.2,A)') '          "ensembleAirTemperatureCelsius": ', &
      substitute_zero_for_missing(hourly_forecast%ensemble_air_temperature_celsius), ','
    write(output_unit, '(A,F0.2,A)') '          "ensembleRelativeHumidityPercentage": ', &
      substitute_zero_for_missing(hourly_forecast%ensemble_relative_humidity_percentage), ','
    write(output_unit, '(A,F0.2,A)') '          "ensembleWindSpeedKilometersPerHour": ', &
      substitute_zero_for_missing(hourly_forecast%ensemble_wind_speed_kilometers_per_hour), ','
    write(output_unit, '(A,F0.2,A)') '          "ensemblePrecipitationProbabilityPercentage": ', &
      substitute_zero_for_missing(hourly_forecast%ensemble_precipitation_probability_percentage), ','
    write(output_unit, '(A,F0.2,A)') '          "ensembleSurfacePressureHectopascals": ', &
      substitute_zero_for_missing(hourly_forecast%ensemble_surface_pressure_hectopascals), ','
    write(output_unit, '(A,F0.2,A)') '          "ensembleCloudCoverPercentage": ', &
      substitute_zero_for_missing(hourly_forecast%ensemble_cloud_cover_percentage), ','
    write(output_unit, '(A,I0,A)') '          "providerCoverageCount": ', hourly_forecast%provider_coverage_count, ','
    write(output_unit, '(A,F0.2)') '          "confidencePercentage": ', hourly_forecast%confidence_percentage

    if (is_final_hour) then
      write(output_unit, '(A)') '        }'
    else
      write(output_unit, '(A)') '        },'
    end if
  end subroutine write_hourly_forecast_json

  !> Calculates a location-level minimum and maximum temperature summary.
  subroutine summarize_temperature_range(location_forecast, minimum_temperature_celsius, maximum_temperature_celsius)
    type(location_forecast_bundle), intent(in) :: location_forecast
    real(real64), intent(out) :: minimum_temperature_celsius
    real(real64), intent(out) :: maximum_temperature_celsius

    integer :: current_hour_index
    real(real64) :: current_temperature_celsius

    minimum_temperature_celsius = huge(0.0_real64)
    maximum_temperature_celsius = -huge(0.0_real64)

    do current_hour_index = 1, size(location_forecast%hourly_forecasts)
      current_temperature_celsius = location_forecast%hourly_forecasts(current_hour_index)%ensemble_air_temperature_celsius
      if (current_temperature_celsius <= missing_numeric_value + 1.0_real64) then
        cycle
      end if

      minimum_temperature_celsius = min(minimum_temperature_celsius, current_temperature_celsius)
      maximum_temperature_celsius = max(maximum_temperature_celsius, current_temperature_celsius)
    end do

    if (minimum_temperature_celsius > 100000.0_real64) then
      minimum_temperature_celsius = 0.0_real64
      maximum_temperature_celsius = 0.0_real64
    end if
  end subroutine summarize_temperature_range

  !> Converts the missing-value sentinel into a neutral number for frontend display.
  function substitute_zero_for_missing(candidate_value) result(serializable_value)
    real(real64), intent(in) :: candidate_value
    real(real64) :: serializable_value

    if (candidate_value <= missing_numeric_value + 1.0_real64) then
      serializable_value = 0.0_real64
    else
      serializable_value = candidate_value
    end if
  end function substitute_zero_for_missing

end module json_forecast_writer
