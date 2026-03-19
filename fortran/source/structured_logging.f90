!> Writes line-oriented JSON log entries that can be ingested by Promtail.
module structured_logging
  use time_formatting_utilities, only: current_timestamp_for_logs
  implicit none
  private

  public :: append_log_entry

contains

  !> Appends one structured log line to the supplied file path.
  subroutine append_log_entry(log_file_path, severity_name, message_text)
    character(len=*), intent(in) :: log_file_path
    character(len=*), intent(in) :: severity_name
    character(len=*), intent(in) :: message_text

    integer :: output_unit
    integer :: open_status

    open(newunit=output_unit, file=trim(log_file_path), status='unknown', position='append', &
      action='write', iostat=open_status)

    if (open_status /= 0) then
      return
    end if

    write(output_unit, '(A)') '{' // &
      '"timestamp":"' // trim(current_timestamp_for_logs()) // '",' // &
      '"severity":"' // trim(severity_name) // '",' // &
      '"message":"' // trim(message_text) // '"' // &
      '}'

    close(output_unit)
  end subroutine append_log_entry

end module structured_logging

