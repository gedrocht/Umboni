"""Beginner-friendly task runner for the Umboni repository.

This module exists for one simple reason: a new contributor should not need to
memorize a long list of unrelated Python, CMake, npm, and documentation
commands just to get productive.

The task runner centralizes the most common repository actions behind plain,
obvious subcommands such as ``doctor``, ``bootstrap``, ``pipeline``, and
``test``. The implementation favors readability over cleverness so a beginner
can open this file, read it from top to bottom, and understand how the project
is stitched together.
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExecutionStep:
    """Represents one shell command that should be shown and then executed."""

    step_name: str
    command_words: tuple[str, ...]
    working_directory: Path


@dataclass(frozen=True)
class ExternalCommandRequirement:
    """Describes a command-line tool the repository depends on."""

    display_name: str
    executable_name: str
    why_it_matters: str
    installation_help_text: str
    is_optional: bool = False


@dataclass(frozen=True)
class RequirementStatus:
    """Stores the result of probing one external command."""

    requirement: ExternalCommandRequirement
    resolved_executable_path: str | None
    version_output: str | None


def determine_repository_root() -> Path:
    """Returns the repository root from the installed package location."""

    return Path(__file__).resolve().parents[2]


def determine_simulator_executable_path(repository_root_directory: Path) -> Path:
    """Returns the expected Fortran simulator path for the current platform."""

    executable_file_name = "new_england_weather_simulator.exe" if os.name == "nt" else "new_england_weather_simulator"
    return repository_root_directory / "build" / "bin" / executable_file_name


def build_external_command_requirements() -> tuple[ExternalCommandRequirement, ...]:
    """Lists the tools a beginner is most likely to need."""

    operating_system_name = platform.system().lower()
    fortran_installation_hint = (
        "Install MSYS2 from https://www.msys2.org/ and then install the UCRT64 "
        "Fortran toolchain with: pacman -S --needed mingw-w64-ucrt-x86_64-gcc-fortran "
        "mingw-w64-ucrt-x86_64-ninja"
        if operating_system_name == "windows"
        else "Install GNU Fortran with your package manager, for example `brew install gcc` or `sudo apt install gfortran`."
    )

    return (
        ExternalCommandRequirement(
            display_name="Python",
            executable_name=Path(sys.executable).name,
            why_it_matters="Needed for the weather fetcher, the task runner, and the documentation tooling.",
            installation_help_text="Install Python 3.10 or newer from https://www.python.org/downloads/.",
        ),
        ExternalCommandRequirement(
            display_name="Node.js",
            executable_name="node",
            why_it_matters="Needed for the repository tooling, Angular dashboard, and Playwright browser tests.",
            installation_help_text="Install Node.js 22 or newer from https://nodejs.org/en/download.",
        ),
        ExternalCommandRequirement(
            display_name="npm",
            executable_name="npm",
            why_it_matters="Needed to install and run the JavaScript tooling in the root repository and frontend workspace.",
            installation_help_text="npm is installed with Node.js. Reinstall Node.js if npm is missing.",
        ),
        ExternalCommandRequirement(
            display_name="CMake",
            executable_name="cmake",
            why_it_matters="Needed to configure the Fortran simulator build.",
            installation_help_text="Install CMake 3.27 or newer from https://cmake.org/download/.",
        ),
        ExternalCommandRequirement(
            display_name="CTest",
            executable_name="ctest",
            why_it_matters="Needed to run the native Fortran tests after the simulator is built.",
            installation_help_text="CTest is installed with CMake. Reinstall CMake if it is missing.",
        ),
        ExternalCommandRequirement(
            display_name="Ninja",
            executable_name="ninja",
            why_it_matters="Needed because the repository's CMake presets use the Ninja generator.",
            installation_help_text=(
                "Install Ninja from https://ninja-build.org/ or through MSYS2, "
                "Homebrew, or your Linux package manager."
            ),
        ),
        ExternalCommandRequirement(
            display_name="GNU Fortran",
            executable_name="gfortran",
            why_it_matters="Needed to compile the Fortran simulation engine.",
            installation_help_text=fortran_installation_hint,
        ),
        ExternalCommandRequirement(
            display_name="Doxygen",
            executable_name="doxygen",
            why_it_matters="Needed to build the reference documentation.",
            installation_help_text="Install Doxygen from https://www.doxygen.nl/download.html.",
        ),
        ExternalCommandRequirement(
            display_name="Docker",
            executable_name="docker",
            why_it_matters="Optional, but useful if you want the observability stack or self-hosted wiki locally.",
            installation_help_text=(
                "Install Docker Desktop from "
                "https://www.docker.com/products/docker-desktop/ if you want "
                "the optional containers."
            ),
            is_optional=True,
        ),
    )


def safely_collect_version_output(command_words: Sequence[str]) -> str | None:
    """Attempts to collect one short version string without failing the caller."""

    try:
        completed_process = subprocess.run(
            command_words,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None

    candidate_output = completed_process.stdout.strip() or completed_process.stderr.strip()
    if not candidate_output:
        return None
    return candidate_output.splitlines()[0]


def collect_requirement_statuses() -> list[RequirementStatus]:
    """Returns the discovered path and version string for each required tool."""

    requirement_statuses: list[RequirementStatus] = []

    for command_requirement in build_external_command_requirements():
        resolved_executable_path = shutil.which(command_requirement.executable_name)
        version_output = None

        if resolved_executable_path is not None:
            if command_requirement.executable_name in {Path(sys.executable).name, "python", "python3"}:
                version_output = safely_collect_version_output((resolved_executable_path, "--version"))
            elif command_requirement.executable_name in {"node", "npm", "cmake", "ctest", "ninja", "gfortran", "doxygen", "docker"}:
                version_output = safely_collect_version_output((resolved_executable_path, "--version"))

        requirement_statuses.append(
            RequirementStatus(
                requirement=command_requirement,
                resolved_executable_path=resolved_executable_path,
                version_output=version_output,
            )
        )

    return requirement_statuses


def print_requirement_statuses(requirement_statuses: Sequence[RequirementStatus]) -> None:
    """Prints a beginner-friendly status report for the external toolchain."""

    print("Umboni prerequisite check")
    print("=========================")

    for requirement_status in requirement_statuses:
        command_requirement = requirement_status.requirement
        if requirement_status.resolved_executable_path is not None:
            print(f"[OK] {command_requirement.display_name}")
            print(f"     Path: {requirement_status.resolved_executable_path}")
            if requirement_status.version_output is not None:
                print(f"     Version: {requirement_status.version_output}")
            print(f"     Why it matters: {command_requirement.why_it_matters}")
        else:
            status_label = "OPTIONAL" if command_requirement.is_optional else "MISSING"
            print(f"[{status_label}] {command_requirement.display_name}")
            print(f"     Why it matters: {command_requirement.why_it_matters}")
            print(f"     How to install it: {command_requirement.installation_help_text}")


def any_required_tools_are_missing(requirement_statuses: Sequence[RequirementStatus]) -> bool:
    """Returns True when a required tool is missing from the current shell."""

    return any(
        requirement_status.resolved_executable_path is None and not requirement_status.requirement.is_optional
        for requirement_status in requirement_statuses
    )


def ensure_artifact_directories_exist(repository_root_directory: Path) -> None:
    """Creates the generated-data and logging directories when they are missing."""

    (repository_root_directory / "artifacts" / "generated").mkdir(parents=True, exist_ok=True)
    (repository_root_directory / "artifacts" / "logs").mkdir(parents=True, exist_ok=True)
    (repository_root_directory / "build" / "doxygen").mkdir(parents=True, exist_ok=True)


def run_execution_steps(
    execution_steps: Sequence[ExecutionStep],
    additional_environment_variables: Mapping[str, str] | None = None,
) -> None:
    """Runs a list of steps while printing clear progress messages."""

    if additional_environment_variables is None:
        additional_environment_variables = {}

    execution_environment = os.environ.copy()
    execution_environment.update(additional_environment_variables)

    for execution_step in execution_steps:
        print()
        print(f"=== {execution_step.step_name} ===")
        print(f"Working directory: {execution_step.working_directory}")
        print(f"Command: {' '.join(execution_step.command_words)}")

        subprocess.run(
            execution_step.command_words,
            check=True,
            cwd=execution_step.working_directory,
            env=execution_environment,
        )


def build_bootstrap_steps(repository_root_directory: Path) -> list[ExecutionStep]:
    """Returns the steps that install the common Python and Node dependencies."""

    return [
        ExecutionStep(
            step_name="Create common artifact directories",
            command_words=(
                sys.executable,
                "-c",
                "from pathlib import Path; "
                "[Path(path).mkdir(parents=True, exist_ok=True) "
                "for path in ('artifacts/generated', 'artifacts/logs', "
                "'build/doxygen')]",
            ),
            working_directory=repository_root_directory,
        ),
        ExecutionStep(
            step_name="Install Python package, test tools, and documentation tools",
            command_words=(sys.executable, "-m", "pip", "install", "-e", ".[dev,docs]"),
            working_directory=repository_root_directory,
        ),
        ExecutionStep(
            step_name="Install repository-level Node tooling",
            command_words=("npm", "ci"),
            working_directory=repository_root_directory,
        ),
        ExecutionStep(
            step_name="Install frontend Node dependencies",
            command_words=("npm", "ci"),
            working_directory=repository_root_directory / "frontend",
        ),
    ]


def build_fortran_build_steps(repository_root_directory: Path) -> list[ExecutionStep]:
    """Returns the steps needed to configure and build the Fortran simulator."""

    return [
        ExecutionStep(
            step_name="Configure the Fortran build with the default preset",
            command_words=("cmake", "--preset", "default"),
            working_directory=repository_root_directory,
        ),
        ExecutionStep(
            step_name="Build the Fortran simulator",
            command_words=("cmake", "--build", "--preset", "default"),
            working_directory=repository_root_directory,
        ),
    ]


def build_simulation_steps(
    repository_root_directory: Path,
    input_csv_path: str,
    output_json_path: str,
    log_file_path: str,
) -> list[ExecutionStep]:
    """Returns the steps that run the Fortran simulator from an existing CSV file."""

    simulator_executable_path = determine_simulator_executable_path(repository_root_directory)

    return [
        *build_fortran_build_steps(repository_root_directory),
        ExecutionStep(
            step_name="Run the Fortran simulator against the normalized provider CSV",
            command_words=(
                str(simulator_executable_path),
                "--skip-fetch",
                "--input-csv",
                input_csv_path,
                "--output-json",
                output_json_path,
                "--log-file",
                log_file_path,
            ),
            working_directory=repository_root_directory,
        ),
        ExecutionStep(
            step_name="Copy the newest forecast JSON into the Angular public data folder",
            command_words=(sys.executable, "scripts/synchronize_generated_forecast_to_frontend.py"),
            working_directory=repository_root_directory,
        ),
    ]


def build_pipeline_steps(
    repository_root_directory: Path,
    output_csv_path: str,
    python_log_file_path: str,
    simulator_log_file_path: str,
    maximum_hours: int,
) -> list[ExecutionStep]:
    """Returns the full data pipeline for beginners who want one command."""

    return [
        ExecutionStep(
            step_name="Fetch provider data for the New England catalog",
            command_words=(
                sys.executable,
                "scripts/run_weather_fetcher.py",
                "--output-csv",
                output_csv_path,
                "--log-file",
                python_log_file_path,
                "--maximum-hours",
                str(maximum_hours),
            ),
            working_directory=repository_root_directory,
        ),
        *build_simulation_steps(
            repository_root_directory=repository_root_directory,
            input_csv_path=output_csv_path,
            output_json_path="artifacts/generated/new-england-forecast.json",
            log_file_path=simulator_log_file_path,
        ),
    ]


def build_repository_test_steps(repository_root_directory: Path) -> list[ExecutionStep]:
    """Returns the repository-level validation steps."""

    return [
        ExecutionStep(
            step_name="Run repository markdown and audit checks",
            command_words=("npm", "run", "validate:repository"),
            working_directory=repository_root_directory,
        )
    ]


def build_python_test_steps(repository_root_directory: Path) -> list[ExecutionStep]:
    """Returns the Python test steps."""

    return [
        ExecutionStep(
            step_name="Run Python unit tests",
            command_words=(sys.executable, "-m", "unittest", "discover", "-s", "python/tests", "-t", "python"),
            working_directory=repository_root_directory,
        )
    ]


def build_fortran_test_steps(repository_root_directory: Path) -> list[ExecutionStep]:
    """Returns the Fortran test steps."""

    return [
        *build_fortran_build_steps(repository_root_directory),
        ExecutionStep(
            step_name="Run the native Fortran test suite",
            command_words=("ctest", "--preset", "default", "--output-on-failure"),
            working_directory=repository_root_directory,
        ),
    ]


def build_frontend_test_steps(
    repository_root_directory: Path,
    include_end_to_end_tests: bool,
) -> list[ExecutionStep]:
    """Returns the frontend validation steps."""

    frontend_directory = repository_root_directory / "frontend"
    frontend_test_steps = [
        ExecutionStep(
            step_name="Run frontend linting",
            command_words=("npm", "run", "lint"),
            working_directory=frontend_directory,
        ),
        ExecutionStep(
            step_name="Run frontend unit tests",
            command_words=("npm", "run", "test"),
            working_directory=frontend_directory,
        ),
        ExecutionStep(
            step_name="Run frontend unit tests with coverage",
            command_words=("npm", "run", "test:coverage"),
            working_directory=frontend_directory,
        ),
        ExecutionStep(
            step_name="Build the Angular dashboard",
            command_words=("npm", "run", "build"),
            working_directory=frontend_directory,
        ),
    ]

    if include_end_to_end_tests:
        frontend_test_steps.extend(
            [
                ExecutionStep(
                    step_name="Install the Chromium browser used by the Playwright smoke tests",
                    command_words=("npx", "playwright", "install", "chromium"),
                    working_directory=frontend_directory,
                ),
                ExecutionStep(
                    step_name="Run the Playwright end-to-end smoke tests",
                    command_words=("npm", "run", "test:e2e"),
                    working_directory=frontend_directory,
                ),
            ]
        )

    return frontend_test_steps


def build_documentation_steps(repository_root_directory: Path, serve_documentation: bool) -> list[ExecutionStep]:
    """Returns the documentation build or serve steps."""

    documentation_steps = [
        ExecutionStep(
            step_name="Generate the Doxygen reference documentation",
            command_words=("doxygen", "Doxyfile"),
            working_directory=repository_root_directory,
        ),
        ExecutionStep(
            step_name="Copy the Doxygen output into the MkDocs site folder",
            command_words=(sys.executable, "scripts/copy_doxygen_output_into_mkdocs.py"),
            working_directory=repository_root_directory,
        ),
    ]

    if serve_documentation:
        documentation_steps.append(
            ExecutionStep(
                step_name="Serve the documentation locally at http://127.0.0.1:8000",
                command_words=("mkdocs", "serve", "--dev-addr", "127.0.0.1:8000"),
                working_directory=repository_root_directory,
            )
        )
    else:
        documentation_steps.append(
            ExecutionStep(
                step_name="Build the documentation site",
                command_words=("mkdocs", "build", "--strict"),
                working_directory=repository_root_directory,
            )
        )

    return documentation_steps


def run_doctor_command() -> int:
    """Checks prerequisites and reports clear install guidance."""

    requirement_statuses = collect_requirement_statuses()
    print_requirement_statuses(requirement_statuses)

    if any_required_tools_are_missing(requirement_statuses):
        print()
        print("One or more required tools are missing.")
        print("Install the missing tools, then run `python scripts/umboni.py doctor` again.")
        return 1

    print()
    print("All required tools were found.")
    print("Next step: run `python scripts/umboni.py bootstrap`.")
    return 0


def run_bootstrap_command(repository_root_directory: Path) -> int:
    """Installs the common Python and Node dependencies."""

    ensure_artifact_directories_exist(repository_root_directory)
    run_execution_steps(build_bootstrap_steps(repository_root_directory))

    print()
    print("Bootstrap finished successfully.")
    print("Next step: run `python scripts/umboni.py pipeline` to generate forecast data.")
    return 0


def run_fetch_command(parsed_arguments: argparse.Namespace, repository_root_directory: Path) -> int:
    """Runs only the Python fetch step."""

    ensure_artifact_directories_exist(repository_root_directory)
    run_execution_steps(
        [
            ExecutionStep(
                step_name="Fetch provider data for the New England catalog",
                command_words=(
                    sys.executable,
                    "scripts/run_weather_fetcher.py",
                    "--output-csv",
                    parsed_arguments.output_csv,
                    "--log-file",
                    parsed_arguments.log_file,
                    "--maximum-hours",
                    str(parsed_arguments.maximum_hours),
                ),
                working_directory=repository_root_directory,
            )
        ]
    )
    print()
    print(f"Fetcher finished. CSV written to {parsed_arguments.output_csv}.")
    return 0


def run_build_fortran_command(repository_root_directory: Path) -> int:
    """Builds the Fortran simulator without running it."""

    ensure_artifact_directories_exist(repository_root_directory)
    run_execution_steps(build_fortran_build_steps(repository_root_directory))
    print()
    print("Fortran simulator build finished successfully.")
    return 0


def run_simulate_command(parsed_arguments: argparse.Namespace, repository_root_directory: Path) -> int:
    """Runs the Fortran simulator from an existing normalized CSV file."""

    ensure_artifact_directories_exist(repository_root_directory)
    run_execution_steps(
        build_simulation_steps(
            repository_root_directory=repository_root_directory,
            input_csv_path=parsed_arguments.input_csv,
            output_json_path=parsed_arguments.output_json,
            log_file_path=parsed_arguments.log_file,
        )
    )
    print()
    print(f"Simulation finished. Forecast JSON written to {parsed_arguments.output_json}.")
    return 0


def run_pipeline_command(parsed_arguments: argparse.Namespace, repository_root_directory: Path) -> int:
    """Runs the full fetch -> simulate -> sync workflow."""

    ensure_artifact_directories_exist(repository_root_directory)
    run_execution_steps(
        build_pipeline_steps(
            repository_root_directory=repository_root_directory,
            output_csv_path=parsed_arguments.output_csv,
            python_log_file_path=parsed_arguments.python_log_file,
            simulator_log_file_path=parsed_arguments.simulator_log_file,
            maximum_hours=parsed_arguments.maximum_hours,
        )
    )
    print()
    print("Pipeline finished successfully.")
    print("The Angular app can now read frontend/public/data/new-england-forecast-sample.json.")
    return 0


def run_frontend_command(parsed_arguments: argparse.Namespace, repository_root_directory: Path) -> int:
    """Starts the Angular development server with beginner-friendly defaults."""

    frontend_directory = repository_root_directory / "frontend"
    run_execution_steps(
        [
            ExecutionStep(
                step_name="Start the Angular development server",
                command_words=("npm", "run", "start", "--", "--host", parsed_arguments.host, "--port", str(parsed_arguments.port)),
                working_directory=frontend_directory,
            )
        ]
    )
    return 0


def run_test_command(parsed_arguments: argparse.Namespace, repository_root_directory: Path) -> int:
    """Runs the requested slice of the test suite."""

    ensure_artifact_directories_exist(repository_root_directory)
    execution_steps: list[ExecutionStep] = []

    if parsed_arguments.scope in {"repository", "all"}:
        execution_steps.extend(build_repository_test_steps(repository_root_directory))
    if parsed_arguments.scope in {"python", "all"}:
        execution_steps.extend(build_python_test_steps(repository_root_directory))
    if parsed_arguments.scope in {"fortran", "all"}:
        execution_steps.extend(build_fortran_test_steps(repository_root_directory))
    if parsed_arguments.scope in {"frontend", "all"}:
        execution_steps.extend(
            build_frontend_test_steps(
                repository_root_directory=repository_root_directory,
                include_end_to_end_tests=not parsed_arguments.skip_end_to_end_tests,
            )
        )
    if parsed_arguments.scope in {"docs", "all"} and not parsed_arguments.skip_documentation_build:
        execution_steps.extend(build_documentation_steps(repository_root_directory, serve_documentation=False))

    run_execution_steps(execution_steps)
    print()
    print("Requested tests finished successfully.")
    return 0


def run_build_docs_command(repository_root_directory: Path) -> int:
    """Builds the documentation site."""

    ensure_artifact_directories_exist(repository_root_directory)
    run_execution_steps(build_documentation_steps(repository_root_directory, serve_documentation=False))
    print()
    print("Documentation site built successfully in the `site/` directory.")
    return 0


def run_serve_docs_command(repository_root_directory: Path) -> int:
    """Serves the documentation site locally."""

    ensure_artifact_directories_exist(repository_root_directory)
    run_execution_steps(build_documentation_steps(repository_root_directory, serve_documentation=True))
    return 0


def build_argument_parser() -> argparse.ArgumentParser:
    """Creates the task runner command-line interface."""

    argument_parser = argparse.ArgumentParser(
        description=(
            "Run the most common Umboni tasks with beginner-friendly commands. "
            "Start with `doctor`, continue with `bootstrap`, then use `pipeline`, "
            "`run-frontend`, and `test all`."
        )
    )
    subparsers = argument_parser.add_subparsers(dest="command_name", required=True)

    subparsers.add_parser("doctor", help="Check whether the required tools are installed.")
    subparsers.add_parser("bootstrap", help="Install the Python and Node dependencies used by the repository.")
    subparsers.add_parser("build-fortran", help="Configure and build the Fortran simulator.")

    fetch_parser = subparsers.add_parser("fetch", help="Fetch provider data and write the normalized CSV file.")
    fetch_parser.add_argument("--output-csv", default="artifacts/generated/provider-observations.csv")
    fetch_parser.add_argument("--log-file", default="artifacts/logs/python-fetcher.log.jsonl")
    fetch_parser.add_argument("--maximum-hours", type=int, default=24)

    simulate_parser = subparsers.add_parser(
        "simulate",
        help="Build the Fortran simulator, run it against an existing CSV file, and synchronize the output to the frontend.",
    )
    simulate_parser.add_argument("--input-csv", default="artifacts/generated/provider-observations.csv")
    simulate_parser.add_argument("--output-json", default="artifacts/generated/new-england-forecast.json")
    simulate_parser.add_argument("--log-file", default="artifacts/logs/fortran-simulator.log.jsonl")

    pipeline_parser = subparsers.add_parser(
        "pipeline",
        help="Run the full fetch -> simulate -> synchronize workflow in one command.",
    )
    pipeline_parser.add_argument("--output-csv", default="artifacts/generated/provider-observations.csv")
    pipeline_parser.add_argument("--python-log-file", default="artifacts/logs/python-fetcher.log.jsonl")
    pipeline_parser.add_argument("--simulator-log-file", default="artifacts/logs/fortran-simulator.log.jsonl")
    pipeline_parser.add_argument("--maximum-hours", type=int, default=24)

    frontend_parser = subparsers.add_parser("run-frontend", help="Start the Angular development server.")
    frontend_parser.add_argument("--host", default="127.0.0.1")
    frontend_parser.add_argument("--port", type=int, default=4200)

    test_parser = subparsers.add_parser("test", help="Run repository tests with one obvious command.")
    test_parser.add_argument("scope", choices=("repository", "python", "fortran", "frontend", "docs", "all"))
    test_parser.add_argument(
        "--skip-end-to-end-tests",
        action="store_true",
        help="Skip Playwright browser installation and the frontend smoke tests.",
    )
    test_parser.add_argument(
        "--skip-documentation-build",
        action="store_true",
        help="Skip the documentation build when the selected scope is `all` or `docs`.",
    )

    subparsers.add_parser("build-docs", help="Build the GitHub Pages documentation site.")
    subparsers.add_parser("serve-docs", help="Serve the documentation site locally with MkDocs.")

    return argument_parser


def main() -> int:
    """Parses arguments, dispatches the requested task, and returns a process exit code."""

    repository_root_directory = determine_repository_root()
    parsed_arguments = build_argument_parser().parse_args()

    if parsed_arguments.command_name == "doctor":
        return run_doctor_command()
    if parsed_arguments.command_name == "bootstrap":
        return run_bootstrap_command(repository_root_directory)
    if parsed_arguments.command_name == "build-fortran":
        return run_build_fortran_command(repository_root_directory)
    if parsed_arguments.command_name == "fetch":
        return run_fetch_command(parsed_arguments, repository_root_directory)
    if parsed_arguments.command_name == "simulate":
        return run_simulate_command(parsed_arguments, repository_root_directory)
    if parsed_arguments.command_name == "pipeline":
        return run_pipeline_command(parsed_arguments, repository_root_directory)
    if parsed_arguments.command_name == "run-frontend":
        return run_frontend_command(parsed_arguments, repository_root_directory)
    if parsed_arguments.command_name == "test":
        return run_test_command(parsed_arguments, repository_root_directory)
    if parsed_arguments.command_name == "build-docs":
        return run_build_docs_command(repository_root_directory)
    if parsed_arguments.command_name == "serve-docs":
        return run_serve_docs_command(repository_root_directory)

    raise ValueError(f"Unsupported command: {parsed_arguments.command_name}")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
