!> Minimal test assertions for plain Fortran executable tests.
module test_support
  use, intrinsic :: iso_fortran_env, only: real64
  implicit none
  private

  public :: assert_equal_integer
  public :: assert_almost_equal_real
  public :: assert_equal_string
  public :: assert_true
  public :: finish_tests

  integer :: accumulated_failure_count = 0

contains

  !> Asserts that two integers are equal.
  subroutine assert_equal_integer(expected_value, actual_value, assertion_message)
    integer, intent(in) :: expected_value
    integer, intent(in) :: actual_value
    character(len=*), intent(in) :: assertion_message

    if (expected_value /= actual_value) then
      accumulated_failure_count = accumulated_failure_count + 1
      write(*, '(A)') 'Assertion failed: ' // trim(assertion_message)
    end if
  end subroutine assert_equal_integer

  !> Asserts that two real numbers are close enough for a deterministic unit test.
  subroutine assert_almost_equal_real(expected_value, actual_value, tolerance_value, assertion_message)
    real(real64), intent(in) :: expected_value
    real(real64), intent(in) :: actual_value
    real(real64), intent(in) :: tolerance_value
    character(len=*), intent(in) :: assertion_message

    if (abs(expected_value - actual_value) > tolerance_value) then
      accumulated_failure_count = accumulated_failure_count + 1
      write(*, '(A)') 'Assertion failed: ' // trim(assertion_message)
    end if
  end subroutine assert_almost_equal_real

  !> Asserts that two trimmed strings are equal.
  subroutine assert_equal_string(expected_value, actual_value, assertion_message)
    character(len=*), intent(in) :: expected_value
    character(len=*), intent(in) :: actual_value
    character(len=*), intent(in) :: assertion_message

    if (trim(expected_value) /= trim(actual_value)) then
      accumulated_failure_count = accumulated_failure_count + 1
      write(*, '(A)') 'Assertion failed: ' // trim(assertion_message)
    end if
  end subroutine assert_equal_string

  !> Asserts that a logical condition is true.
  subroutine assert_true(condition_is_true, assertion_message)
    logical, intent(in) :: condition_is_true
    character(len=*), intent(in) :: assertion_message

    if (.not. condition_is_true) then
      accumulated_failure_count = accumulated_failure_count + 1
      write(*, '(A)') 'Assertion failed: ' // trim(assertion_message)
    end if
  end subroutine assert_true

  !> Exits the program with a non-zero status code when any assertion failed.
  subroutine finish_tests()
    if (accumulated_failure_count > 0) then
      error stop 'At least one Fortran test assertion failed.'
    end if
  end subroutine finish_tests

end module test_support
