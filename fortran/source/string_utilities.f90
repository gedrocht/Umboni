!> Supplies helper routines for line splitting and numeric parsing.
module string_utilities
  use, intrinsic :: iso_fortran_env, only: real64
  implicit none
  private

  public :: split_comma_separated_line
  public :: parse_real_value
  public :: parse_integer_value
  public :: trim_whitespace

contains

  !> Splits a simple comma-separated line into preallocated fields.
  subroutine split_comma_separated_line(comma_separated_line, split_fields)
    character(len=*), intent(in) :: comma_separated_line
    character(len=*), dimension(:), intent(out) :: split_fields

    integer :: current_character_index
    integer :: current_field_index
    integer :: field_start_index
    integer :: final_character_index

    split_fields = ''
    current_field_index = 1
    field_start_index = 1
    final_character_index = len_trim(comma_separated_line)

    do current_character_index = 1, final_character_index
      if (comma_separated_line(current_character_index:current_character_index) == ',') then
        if (current_field_index <= size(split_fields)) then
          split_fields(current_field_index) = trim_whitespace( &
            comma_separated_line(field_start_index:current_character_index - 1) &
          )
        end if

        current_field_index = current_field_index + 1
        field_start_index = current_character_index + 1
      end if
    end do

    if (current_field_index <= size(split_fields) .and. field_start_index <= final_character_index) then
      split_fields(current_field_index) = trim_whitespace( &
        comma_separated_line(field_start_index:final_character_index) &
      )
    else if (current_field_index <= size(split_fields)) then
      split_fields(current_field_index) = ''
    end if
  end subroutine split_comma_separated_line

  !> Removes leading and trailing spaces from a character value.
  function trim_whitespace(untrimmed_value) result(trimmed_value)
    character(len=*), intent(in) :: untrimmed_value
    character(len=len(untrimmed_value)) :: trimmed_value

    trimmed_value = adjustl(trim(untrimmed_value))
  end function trim_whitespace

  !> Parses a floating-point number and falls back to a caller-supplied default.
  function parse_real_value(character_value, fallback_value) result(parsed_value)
    character(len=*), intent(in) :: character_value
    real(real64), intent(in) :: fallback_value
    real(real64) :: parsed_value

    integer :: input_output_status

    parsed_value = fallback_value
    if (len_trim(character_value) == 0) then
      return
    end if

    read(character_value, *, iostat=input_output_status) parsed_value
    if (input_output_status /= 0) then
      parsed_value = fallback_value
    end if
  end function parse_real_value

  !> Parses an integer and falls back to a caller-supplied default.
  function parse_integer_value(character_value, fallback_value) result(parsed_value)
    character(len=*), intent(in) :: character_value
    integer, intent(in) :: fallback_value
    integer :: parsed_value

    integer :: input_output_status

    parsed_value = fallback_value
    if (len_trim(character_value) == 0) then
      return
    end if

    read(character_value, *, iostat=input_output_status) parsed_value
    if (input_output_status /= 0) then
      parsed_value = fallback_value
    end if
  end function parse_integer_value

end module string_utilities

