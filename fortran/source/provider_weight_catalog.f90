!> Centralizes the relative trust assigned to each weather provider.
module provider_weight_catalog
  use, intrinsic :: iso_fortran_env, only: real64
  implicit none
  private

  public :: provider_weight
  public :: supported_provider_count

contains

  !> Returns how many providers the ensemble logic expects when calculating confidence.
  integer function supported_provider_count()
    supported_provider_count = 4
  end function supported_provider_count

  !> Returns a weighting factor for the supplied provider name.
  function provider_weight(provider_name) result(weight_value)
    character(len=*), intent(in) :: provider_name
    real(real64) :: weight_value

    select case (trim(provider_name))
    case ('Open-Meteo')
      weight_value = 0.30_real64
    case ('National Weather Service')
      weight_value = 0.30_real64
    case ('MET Norway')
      weight_value = 0.25_real64
    case ('7Timer')
      weight_value = 0.15_real64
    case default
      weight_value = 0.10_real64
    end select
  end function provider_weight

end module provider_weight_catalog

