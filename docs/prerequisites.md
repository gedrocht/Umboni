# Prerequisites

This page is written for a complete beginner.

Your goal is simple: install the tools that Umboni needs, then verify them with
one command:

```bash
python scripts/umboni.py doctor
```

## Required tools

You need these tools for the core project:

- Python 3.10 or newer
- Node.js 22 or newer
- npm
- CMake 3.27 or newer
- Ninja
- GNU Fortran (`gfortran`)
- Doxygen

You only need Docker if you want the optional wiki or observability stack.

## Windows

Install these first:

- Python: [python.org/downloads](https://www.python.org/downloads/)
- Node.js: [nodejs.org/en/download](https://nodejs.org/en/download)
- CMake: [cmake.org/download](https://cmake.org/download/)
- MSYS2: [msys2.org](https://www.msys2.org/)
- Doxygen: [doxygen.nl/download.html](https://www.doxygen.nl/download.html)

After MSYS2 is installed, open the **MSYS2 UCRT64** shell and run:

```bash
pacman -Syu
pacman -S --needed mingw-w64-ucrt-x86_64-gcc-fortran mingw-w64-ucrt-x86_64-ninja
```

Then make sure this folder is on your Windows `PATH`:

```text
C:\msys64\ucrt64\bin
```

Why that matters:

- `gfortran.exe` lives there
- `ninja.exe` lives there

## macOS

Install the Apple command-line tools first:

```bash
xcode-select --install
```

Then install the project prerequisites with Homebrew:

```bash
brew install python node cmake ninja gcc doxygen
```

`gcc` supplies GNU Fortran on macOS.

## Ubuntu and Debian

Install the native build tools with:

```bash
sudo apt update
sudo apt install -y python3 python3-pip cmake ninja-build gfortran doxygen
```

For Node.js, use the official download page:

- Node.js: [nodejs.org/en/download](https://nodejs.org/en/download)

That keeps the beginner instructions simple and makes it easier to stay on the
Node 22 line that the repository expects.

## Optional tools

These are not required for the core app:

- Docker Desktop or Docker Engine for the wiki and observability stack
- GitHub CLI if you want to work with pull requests from the terminal

## Verify everything

After installing the tools, go back to the repository root and run:

```bash
python scripts/umboni.py doctor
```

What good looks like:

- every required tool is listed as `[OK]`
- the command tells you to run `python scripts/umboni.py bootstrap`

If one tool is still missing, fix that single tool and run `doctor` again.
