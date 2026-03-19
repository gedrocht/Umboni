!> Defines the core data structures used by the Fortran simulation engine.
module weather_data_types
  use, intrinsic :: iso_fortran_env, only: real64
  implicit none
  private

  integer, parameter, public :: text_field_length = 128
  integer, parameter, public :: timestamp_length = 32
  integer, parameter, public :: simulated_hour_count = 24
  real(real64), parameter, public :: missing_numeric_value = -9999.0_real64

  !> Holds one normalized hourly observation from one provider.
  type, public :: provider_hourly_forecast_record
    character(len=text_field_length) :: provider_name = ''
    character(len=text_field_length) :: state_name = ''
    character(len=text_field_length) :: location_name = ''
    real(real64) :: latitude_degrees = 0.0_real64
    real(real64) :: longitude_degrees = 0.0_real64
    real(real64) :: altitude_meters = 0.0_real64
    integer :: forecast_hour_offset = 0
    character(len=timestamp_length) :: forecast_timestamp_utc = ''
    real(real64) :: air_temperature_celsius = missing_numeric_value
    real(real64) :: relative_humidity_percentage = missing_numeric_value
    real(real64) :: wind_speed_kilometers_per_hour = missing_numeric_value
    real(real64) :: precipitation_probability_percentage = missing_numeric_value
    real(real64) :: surface_pressure_hectopascals = missing_numeric_value
    real(real64) :: cloud_cover_percentage = missing_numeric_value
  end type provider_hourly_forecast_record

  !> Holds one simulated hourly forecast after multiple providers are combined.
  type, public :: hourly_regional_forecast
    integer :: forecast_hour_offset = 0
    character(len=timestamp_length) :: forecast_timestamp_utc = ''
    real(real64) :: ensemble_air_temperature_celsius = missing_numeric_value
    real(real64) :: ensemble_relative_humidity_percentage = missing_numeric_value
    real(real64) :: ensemble_wind_speed_kilometers_per_hour = missing_numeric_value
    real(real64) :: ensemble_precipitation_probability_percentage = missing_numeric_value
    real(real64) :: ensemble_surface_pressure_hectopascals = missing_numeric_value
    real(real64) :: ensemble_cloud_cover_percentage = missing_numeric_value
    integer :: provider_coverage_count = 0
    real(real64) :: confidence_percentage = 0.0_real64
  end type hourly_regional_forecast

  !> Holds the forecast for one named New England location.
  type, public :: location_forecast_bundle
    character(len=text_field_length) :: state_name = ''
    character(len=text_field_length) :: location_name = ''
    real(real64) :: latitude_degrees = 0.0_real64
    real(real64) :: longitude_degrees = 0.0_real64
    type(hourly_regional_forecast), allocatable :: hourly_forecasts(:)
  end type location_forecast_bundle

end module weather_data_types

