!> Combines provider records into a simple but deterministic 24-hour ensemble forecast.
module forecast_consensus_engine
  use, intrinsic :: iso_fortran_env, only: real64
  use provider_weight_catalog, only: provider_weight, supported_provider_count
  use weather_data_types, only: &
    hourly_regional_forecast, &
    location_forecast_bundle, &
    missing_numeric_value, &
    provider_hourly_forecast_record, &
    simulated_hour_count
  implicit none
  private

  public :: build_location_forecasts

  type :: hourly_aggregation_state
    real(real64) :: air_temperature_weighted_sum = 0.0_real64
    real(real64) :: air_temperature_weight_total = 0.0_real64
    real(real64) :: relative_humidity_weighted_sum = 0.0_real64
    real(real64) :: relative_humidity_weight_total = 0.0_real64
    real(real64) :: wind_speed_weighted_sum = 0.0_real64
    real(real64) :: wind_speed_weight_total = 0.0_real64
    real(real64) :: precipitation_probability_weighted_sum = 0.0_real64
    real(real64) :: precipitation_probability_weight_total = 0.0_real64
    real(real64) :: surface_pressure_weighted_sum = 0.0_real64
    real(real64) :: surface_pressure_weight_total = 0.0_real64
    real(real64) :: cloud_cover_weighted_sum = 0.0_real64
    real(real64) :: cloud_cover_weight_total = 0.0_real64
    integer :: provider_coverage_count = 0
    character(len=32) :: forecast_timestamp_utc = ''
  end type hourly_aggregation_state

  type :: location_aggregation_bundle
    character(len=128) :: state_name = ''
    character(len=128) :: location_name = ''
    real(real64) :: latitude_degrees = 0.0_real64
    real(real64) :: longitude_degrees = 0.0_real64
    type(hourly_aggregation_state) :: hourly_states(simulated_hour_count)
  end type location_aggregation_bundle

contains

  !> Builds one 24-hour forecast bundle per location found in the provider records.
  subroutine build_location_forecasts(provider_records, location_forecasts)
    type(provider_hourly_forecast_record), intent(in) :: provider_records(:)
    type(location_forecast_bundle), allocatable, intent(out) :: location_forecasts(:)

    type(location_aggregation_bundle), allocatable :: aggregation_bundles(:)
    integer :: bundle_count
    integer :: current_record_index
    integer :: located_bundle_index

    allocate(aggregation_bundles(size(provider_records)))
    bundle_count = 0

    do current_record_index = 1, size(provider_records)
      located_bundle_index = find_or_create_bundle(aggregation_bundles, bundle_count, provider_records(current_record_index))
      call accumulate_provider_record(aggregation_bundles(located_bundle_index), provider_records(current_record_index))
    end do

    allocate(location_forecasts(bundle_count))
    do current_record_index = 1, bundle_count
      call convert_aggregation_to_public_forecast(aggregation_bundles(current_record_index), location_forecasts(current_record_index))
    end do
  end subroutine build_location_forecasts

  !> Locates an existing location bundle or creates a new one.
  integer function find_or_create_bundle(aggregation_bundles, bundle_count, provider_record)
    type(location_aggregation_bundle), intent(inout) :: aggregation_bundles(:)
    integer, intent(inout) :: bundle_count
    type(provider_hourly_forecast_record), intent(in) :: provider_record

    integer :: current_bundle_index

    do current_bundle_index = 1, bundle_count
      if (trim(aggregation_bundles(current_bundle_index)%state_name) == trim(provider_record%state_name) .and. &
          trim(aggregation_bundles(current_bundle_index)%location_name) == trim(provider_record%location_name)) then
        find_or_create_bundle = current_bundle_index
        return
      end if
    end do

    bundle_count = bundle_count + 1
    aggregation_bundles(bundle_count)%state_name = provider_record%state_name
    aggregation_bundles(bundle_count)%location_name = provider_record%location_name
    aggregation_bundles(bundle_count)%latitude_degrees = provider_record%latitude_degrees
    aggregation_bundles(bundle_count)%longitude_degrees = provider_record%longitude_degrees
    find_or_create_bundle = bundle_count
  end function find_or_create_bundle

  !> Adds one provider record into the correct hourly aggregation bucket.
  subroutine accumulate_provider_record(location_bundle, provider_record)
    type(location_aggregation_bundle), intent(inout) :: location_bundle
    type(provider_hourly_forecast_record), intent(in) :: provider_record

    integer :: hour_index
    real(real64) :: current_provider_weight

    hour_index = provider_record%forecast_hour_offset
    if (hour_index < 1 .or. hour_index > simulated_hour_count) then
      return
    end if

    current_provider_weight = provider_weight(provider_record%provider_name)

    if (len_trim(location_bundle%hourly_states(hour_index)%forecast_timestamp_utc) == 0) then
      location_bundle%hourly_states(hour_index)%forecast_timestamp_utc = provider_record%forecast_timestamp_utc
    end if

    location_bundle%hourly_states(hour_index)%provider_coverage_count = &
      location_bundle%hourly_states(hour_index)%provider_coverage_count + 1

    call accumulate_value(provider_record%air_temperature_celsius, current_provider_weight, &
      location_bundle%hourly_states(hour_index)%air_temperature_weighted_sum, &
      location_bundle%hourly_states(hour_index)%air_temperature_weight_total)
    call accumulate_value(provider_record%relative_humidity_percentage, current_provider_weight, &
      location_bundle%hourly_states(hour_index)%relative_humidity_weighted_sum, &
      location_bundle%hourly_states(hour_index)%relative_humidity_weight_total)
    call accumulate_value(provider_record%wind_speed_kilometers_per_hour, current_provider_weight, &
      location_bundle%hourly_states(hour_index)%wind_speed_weighted_sum, &
      location_bundle%hourly_states(hour_index)%wind_speed_weight_total)
    call accumulate_value(provider_record%precipitation_probability_percentage, current_provider_weight, &
      location_bundle%hourly_states(hour_index)%precipitation_probability_weighted_sum, &
      location_bundle%hourly_states(hour_index)%precipitation_probability_weight_total)
    call accumulate_value(provider_record%surface_pressure_hectopascals, current_provider_weight, &
      location_bundle%hourly_states(hour_index)%surface_pressure_weighted_sum, &
      location_bundle%hourly_states(hour_index)%surface_pressure_weight_total)
    call accumulate_value(provider_record%cloud_cover_percentage, current_provider_weight, &
      location_bundle%hourly_states(hour_index)%cloud_cover_weighted_sum, &
      location_bundle%hourly_states(hour_index)%cloud_cover_weight_total)
  end subroutine accumulate_provider_record

  !> Adds one numeric input to a weighted sum if the value is present.
  subroutine accumulate_value(numeric_value, weight_value, weighted_sum, weight_total)
    real(real64), intent(in) :: numeric_value
    real(real64), intent(in) :: weight_value
    real(real64), intent(inout) :: weighted_sum
    real(real64), intent(inout) :: weight_total

    if (numeric_value <= missing_numeric_value + 1.0_real64) then
      return
    end if

    weighted_sum = weighted_sum + (numeric_value * weight_value)
    weight_total = weight_total + weight_value
  end subroutine accumulate_value

  !> Converts private aggregation state into the public forecast type.
  subroutine convert_aggregation_to_public_forecast(aggregation_bundle, public_forecast_bundle)
    type(location_aggregation_bundle), intent(in) :: aggregation_bundle
    type(location_forecast_bundle), intent(out) :: public_forecast_bundle

    integer :: current_hour_index

    public_forecast_bundle%state_name = aggregation_bundle%state_name
    public_forecast_bundle%location_name = aggregation_bundle%location_name
    public_forecast_bundle%latitude_degrees = aggregation_bundle%latitude_degrees
    public_forecast_bundle%longitude_degrees = aggregation_bundle%longitude_degrees
    allocate(public_forecast_bundle%hourly_forecasts(simulated_hour_count))

    do current_hour_index = 1, simulated_hour_count
      public_forecast_bundle%hourly_forecasts(current_hour_index)%forecast_hour_offset = current_hour_index
      public_forecast_bundle%hourly_forecasts(current_hour_index)%forecast_timestamp_utc = &
        aggregation_bundle%hourly_states(current_hour_index)%forecast_timestamp_utc
      public_forecast_bundle%hourly_forecasts(current_hour_index)%provider_coverage_count = &
        aggregation_bundle%hourly_states(current_hour_index)%provider_coverage_count
      public_forecast_bundle%hourly_forecasts(current_hour_index)%confidence_percentage = &
        100.0_real64 * real(aggregation_bundle%hourly_states(current_hour_index)%provider_coverage_count, real64) / &
        real(supported_provider_count(), real64)

      public_forecast_bundle%hourly_forecasts(current_hour_index)%ensemble_air_temperature_celsius = &
        smooth_against_previous_hour( &
          resolve_weighted_average(aggregation_bundle%hourly_states(current_hour_index)%air_temperature_weighted_sum, &
            aggregation_bundle%hourly_states(current_hour_index)%air_temperature_weight_total), &
          current_hour_index, public_forecast_bundle%hourly_forecasts, 'temperature')
      public_forecast_bundle%hourly_forecasts(current_hour_index)%ensemble_relative_humidity_percentage = &
        resolve_weighted_average(aggregation_bundle%hourly_states(current_hour_index)%relative_humidity_weighted_sum, &
          aggregation_bundle%hourly_states(current_hour_index)%relative_humidity_weight_total)
      public_forecast_bundle%hourly_forecasts(current_hour_index)%ensemble_wind_speed_kilometers_per_hour = &
        smooth_against_previous_hour( &
          resolve_weighted_average(aggregation_bundle%hourly_states(current_hour_index)%wind_speed_weighted_sum, &
            aggregation_bundle%hourly_states(current_hour_index)%wind_speed_weight_total), &
          current_hour_index, public_forecast_bundle%hourly_forecasts, 'wind')
      public_forecast_bundle%hourly_forecasts(current_hour_index)%ensemble_precipitation_probability_percentage = &
        resolve_weighted_average(aggregation_bundle%hourly_states(current_hour_index)%precipitation_probability_weighted_sum, &
          aggregation_bundle%hourly_states(current_hour_index)%precipitation_probability_weight_total)
      public_forecast_bundle%hourly_forecasts(current_hour_index)%ensemble_surface_pressure_hectopascals = &
        resolve_weighted_average(aggregation_bundle%hourly_states(current_hour_index)%surface_pressure_weighted_sum, &
          aggregation_bundle%hourly_states(current_hour_index)%surface_pressure_weight_total)
      public_forecast_bundle%hourly_forecasts(current_hour_index)%ensemble_cloud_cover_percentage = &
        resolve_weighted_average(aggregation_bundle%hourly_states(current_hour_index)%cloud_cover_weighted_sum, &
          aggregation_bundle%hourly_states(current_hour_index)%cloud_cover_weight_total)
    end do
  end subroutine convert_aggregation_to_public_forecast

  !> Resolves a weighted average, or returns the missing sentinel when no provider had data.
  function resolve_weighted_average(weighted_sum, weight_total) result(resolved_value)
    real(real64), intent(in) :: weighted_sum
    real(real64), intent(in) :: weight_total
    real(real64) :: resolved_value

    if (weight_total <= 0.0_real64) then
      resolved_value = missing_numeric_value
    else
      resolved_value = weighted_sum / weight_total
    end if
  end function resolve_weighted_average

  !> Applies gentle smoothing to reduce unrealistic hour-to-hour jumps in the public output.
  function smooth_against_previous_hour(current_value, current_hour_index, hourly_forecasts, quantity_name) result(smoothed_value)
    real(real64), intent(in) :: current_value
    integer, intent(in) :: current_hour_index
    type(hourly_regional_forecast), intent(in) :: hourly_forecasts(:)
    character(len=*), intent(in) :: quantity_name
    real(real64) :: smoothed_value

    real(real64) :: previous_value

    smoothed_value = current_value

    if (current_hour_index == 1) then
      return
    end if

    select case (trim(quantity_name))
    case ('temperature')
      previous_value = hourly_forecasts(current_hour_index - 1)%ensemble_air_temperature_celsius
    case ('wind')
      previous_value = hourly_forecasts(current_hour_index - 1)%ensemble_wind_speed_kilometers_per_hour
    case default
      previous_value = missing_numeric_value
    end select

    if (current_value <= missing_numeric_value + 1.0_real64 .or. previous_value <= missing_numeric_value + 1.0_real64) then
      return
    end if

    smoothed_value = (0.75_real64 * current_value) + (0.25_real64 * previous_value)
  end function smooth_against_previous_hour

end module forecast_consensus_engine
