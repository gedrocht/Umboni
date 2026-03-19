!> Provides tiny time-formatting helpers for log files.
module time_formatting_utilities
  implicit none
  private

  public :: current_timestamp_for_logs

contains

  !> Returns the current local date and time in an ISO-like form.
  function current_timestamp_for_logs() result(formatted_timestamp)
    character(len=32) :: formatted_timestamp
    integer :: date_time_components(8)

    call date_and_time(values=date_time_components)

    write( &
      formatted_timestamp, &
      '(I4.4,"-",I2.2,"-",I2.2,"T",I2.2,":",I2.2,":",I2.2)' &
    ) &
      date_time_components(1), &
      date_time_components(2), &
      date_time_components(3), &
      date_time_components(5), &
      date_time_components(6), &
      date_time_components(7)
  end function current_timestamp_for_logs

end module time_formatting_utilities

