!> Parses a small set of command-line flags for the simulation executable.
module command_line_argument_parser
  implicit none
  private

  public :: simulation_command_line_options
  public :: parse_command_line_options

  type :: simulation_command_line_options
    character(len=256) :: input_csv_path = 'artifacts/generated/provider-observations.csv'
    character(len=256) :: output_json_path = 'artifacts/generated/new-england-forecast.json'
    character(len=256) :: log_file_path = 'artifacts/logs/fortran-simulator.log.jsonl'
    character(len=256) :: python_command = 'python'
    logical :: skip_fetch = .false.
  end type simulation_command_line_options

contains

  !> Parses command-line flags into a single options record.
  function parse_command_line_options() result(parsed_options)
    type(simulation_command_line_options) :: parsed_options

    integer :: argument_count
    integer :: current_argument_index
    character(len=256) :: current_argument_value

    argument_count = command_argument_count()
    current_argument_index = 1

    do while (current_argument_index <= argument_count)
      call get_command_argument(current_argument_index, current_argument_value)

      select case (trim(current_argument_value))
      case ('--input-csv')
        current_argument_index = current_argument_index + 1
        call get_command_argument(current_argument_index, parsed_options%input_csv_path)
      case ('--output-json')
        current_argument_index = current_argument_index + 1
        call get_command_argument(current_argument_index, parsed_options%output_json_path)
      case ('--log-file')
        current_argument_index = current_argument_index + 1
        call get_command_argument(current_argument_index, parsed_options%log_file_path)
      case ('--python-command')
        current_argument_index = current_argument_index + 1
        call get_command_argument(current_argument_index, parsed_options%python_command)
      case ('--skip-fetch')
        parsed_options%skip_fetch = .true.
      case default
        continue
      end select

      current_argument_index = current_argument_index + 1
    end do
  end function parse_command_line_options

end module command_line_argument_parser

