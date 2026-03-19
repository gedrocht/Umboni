if(CMAKE_Fortran_COMPILER_ID STREQUAL "GNU")
  if(ENABLE_STRICT_FORTRAN_WARNINGS)
    add_compile_options(
      -Wall
      -Wextra
      -Wpedantic
      -Wimplicit-interface
      -Werror
      -fimplicit-none
      -fcheck=all
      -fbacktrace
      -ffpe-trap=invalid,zero,overflow
    )
  endif()

  if(ENABLE_FORTRAN_ADDRESS_SANITIZER)
    add_compile_options(-fsanitize=address,undefined -fno-omit-frame-pointer)
    add_link_options(-fsanitize=address,undefined)
  endif()

  if(ENABLE_FORTRAN_COVERAGE)
    add_compile_options(--coverage)
    add_link_options(--coverage)
  endif()
endif()

