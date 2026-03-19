"""Tests for the beginner-friendly repository task runner."""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
from argparse import Namespace
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from new_england_weather_data_fetcher.beginner_workflow import (
    ExecutionStep,
    ExternalCommandRequirement,
    RequirementStatus,
    any_required_tools_are_missing,
    build_argument_parser,
    build_bootstrap_steps,
    build_documentation_steps,
    build_external_command_requirements,
    build_fortran_build_steps,
    build_fortran_test_steps,
    build_frontend_test_steps,
    build_pipeline_steps,
    build_python_test_steps,
    build_repository_test_steps,
    build_simulation_steps,
    collect_requirement_statuses,
    determine_repository_root,
    determine_simulator_executable_path,
    ensure_artifact_directories_exist,
    main,
    print_requirement_statuses,
    run_bootstrap_command,
    run_build_docs_command,
    run_build_fortran_command,
    run_doctor_command,
    run_execution_steps,
    run_fetch_command,
    run_frontend_command,
    run_pipeline_command,
    run_serve_docs_command,
    run_simulate_command,
    run_test_command,
    safely_collect_version_output,
)


class BeginnerWorkflowTests(unittest.TestCase):
    """Covers the command construction and dispatch used by the task runner."""

    def setUp(self) -> None:
        """Creates a stable repository-root path for command-construction tests."""

        self.repository_root_directory = Path("/umboni-repository")

    def test_determine_repository_root_returns_the_workspace_root(self) -> None:
        """Ensures the repository-root helper resolves to the checkout root."""

        repository_root_directory = determine_repository_root()

        self.assertTrue((repository_root_directory / "README.md").exists())
        self.assertTrue((repository_root_directory / "pyproject.toml").exists())

    def test_determine_simulator_executable_path_uses_windows_suffix_on_windows(self) -> None:
        """Ensures Windows users receive the `.exe` simulator path."""

        with patch("new_england_weather_data_fetcher.beginner_workflow.os.name", "nt"):
            simulator_executable_path = determine_simulator_executable_path(self.repository_root_directory)

        self.assertEqual(
            self.repository_root_directory / "build" / "bin" / "new_england_weather_simulator.exe",
            simulator_executable_path,
        )

    def test_determine_simulator_executable_path_uses_plain_name_on_non_windows_platforms(self) -> None:
        """Ensures Unix-like users receive the platform-appropriate executable path."""

        with patch("new_england_weather_data_fetcher.beginner_workflow.os.name", "posix"):
            simulator_executable_path = determine_simulator_executable_path(self.repository_root_directory)

        self.assertEqual(
            self.repository_root_directory / "build" / "bin" / "new_england_weather_simulator",
            simulator_executable_path,
        )

    def test_build_external_command_requirements_uses_windows_specific_fortran_guidance(self) -> None:
        """Ensures Windows users are pointed toward the MSYS2 setup path."""

        with patch("new_england_weather_data_fetcher.beginner_workflow.platform.system", return_value="Windows"):
            requirements = build_external_command_requirements()

        fortran_requirement = next(
            requirement for requirement in requirements if requirement.display_name == "GNU Fortran"
        )
        docker_requirement = next(requirement for requirement in requirements if requirement.display_name == "Docker")

        self.assertIn("MSYS2", fortran_requirement.installation_help_text)
        self.assertTrue(docker_requirement.is_optional)

    def test_build_external_command_requirements_uses_unix_fortran_guidance_off_windows(self) -> None:
        """Ensures non-Windows users receive the Unix-like Fortran guidance."""

        with patch("new_england_weather_data_fetcher.beginner_workflow.platform.system", return_value="Linux"):
            requirements = build_external_command_requirements()

        fortran_requirement = next(
            requirement for requirement in requirements if requirement.display_name == "GNU Fortran"
        )

        self.assertIn("brew install gcc", fortran_requirement.installation_help_text)

    def test_safely_collect_version_output_returns_the_first_output_line(self) -> None:
        """Ensures the helper returns the first non-empty version line."""

        completed_process = SimpleNamespace(stdout="tool 1.2.3\nsecond line\n", stderr="")
        with patch("new_england_weather_data_fetcher.beginner_workflow.subprocess.run", return_value=completed_process):
            version_output = safely_collect_version_output(("tool", "--version"))

        self.assertEqual("tool 1.2.3", version_output)

    def test_safely_collect_version_output_can_fall_back_to_stderr(self) -> None:
        """Ensures the helper reads stderr when stdout is empty."""

        completed_process = SimpleNamespace(stdout="", stderr="tool 1.2.3\nwarning")
        with patch("new_england_weather_data_fetcher.beginner_workflow.subprocess.run", return_value=completed_process):
            version_output = safely_collect_version_output(("tool", "--version"))

        self.assertEqual("tool 1.2.3", version_output)

    def test_safely_collect_version_output_returns_none_for_empty_output(self) -> None:
        """Ensures the helper returns None when no version text is available."""

        completed_process = SimpleNamespace(stdout="", stderr="")
        with patch("new_england_weather_data_fetcher.beginner_workflow.subprocess.run", return_value=completed_process):
            version_output = safely_collect_version_output(("tool", "--version"))

        self.assertIsNone(version_output)

    def test_safely_collect_version_output_returns_none_when_execution_fails(self) -> None:
        """Ensures probing a missing executable does not crash the caller."""

        with patch(
            "new_england_weather_data_fetcher.beginner_workflow.subprocess.run",
            side_effect=OSError("not found"),
        ):
            version_output = safely_collect_version_output(("tool", "--version"))

        self.assertIsNone(version_output)

    def test_collect_requirement_statuses_captures_paths_and_versions(self) -> None:
        """Ensures prerequisite discovery combines `which` lookups and version probes."""

        python_requirement = ExternalCommandRequirement(
            display_name="Python",
            executable_name="python",
            why_it_matters="python reason",
            installation_help_text="python install",
        )
        custom_requirement = ExternalCommandRequirement(
            display_name="Custom",
            executable_name="custom-tool",
            why_it_matters="custom reason",
            installation_help_text="custom install",
        )

        with patch(
            "new_england_weather_data_fetcher.beginner_workflow.build_external_command_requirements",
            return_value=(python_requirement, custom_requirement),
        ), patch(
            "new_england_weather_data_fetcher.beginner_workflow.shutil.which",
            side_effect=["/usr/bin/python", None],
        ), patch(
            "new_england_weather_data_fetcher.beginner_workflow.safely_collect_version_output",
            return_value="Python 3.12.0",
        ):
            requirement_statuses = collect_requirement_statuses()

        self.assertEqual("/usr/bin/python", requirement_statuses[0].resolved_executable_path)
        self.assertEqual("Python 3.12.0", requirement_statuses[0].version_output)
        self.assertIsNone(requirement_statuses[1].resolved_executable_path)
        self.assertIsNone(requirement_statuses[1].version_output)

    def test_collect_requirement_statuses_captures_versions_for_node_like_tools(self) -> None:
        """Ensures non-Python tools still receive version probing when present."""

        node_requirement = ExternalCommandRequirement(
            display_name="Node.js",
            executable_name="node",
            why_it_matters="Runs the frontend.",
            installation_help_text="Install Node.js.",
        )

        with patch(
            "new_england_weather_data_fetcher.beginner_workflow.build_external_command_requirements",
            return_value=(node_requirement,),
        ), patch(
            "new_england_weather_data_fetcher.beginner_workflow.shutil.which",
            return_value="/usr/bin/node",
        ), patch(
            "new_england_weather_data_fetcher.beginner_workflow.safely_collect_version_output",
            return_value="v22.0.0",
        ) as collect_version:
            requirement_statuses = collect_requirement_statuses()

        collect_version.assert_called_once_with(("/usr/bin/node", "--version"))
        self.assertEqual("v22.0.0", requirement_statuses[0].version_output)

    def test_collect_requirement_statuses_skips_unknown_present_tools_without_known_version_flags(self) -> None:
        """Ensures present but unknown tools do not trigger unnecessary version probes."""

        custom_requirement = ExternalCommandRequirement(
            display_name="Custom",
            executable_name="custom-tool",
            why_it_matters="Runs something custom.",
            installation_help_text="Install the custom tool.",
        )

        with patch(
            "new_england_weather_data_fetcher.beginner_workflow.build_external_command_requirements",
            return_value=(custom_requirement,),
        ), patch(
            "new_england_weather_data_fetcher.beginner_workflow.shutil.which",
            return_value="/usr/bin/custom-tool",
        ), patch(
            "new_england_weather_data_fetcher.beginner_workflow.safely_collect_version_output"
        ) as collect_version:
            requirement_statuses = collect_requirement_statuses()

        collect_version.assert_not_called()
        self.assertEqual("/usr/bin/custom-tool", requirement_statuses[0].resolved_executable_path)
        self.assertIsNone(requirement_statuses[0].version_output)

    def test_print_requirement_statuses_prints_present_and_missing_tools(self) -> None:
        """Ensures the doctor output is understandable for both success and failure cases."""

        present_requirement = RequirementStatus(
            requirement=ExternalCommandRequirement(
                display_name="Python",
                executable_name="python",
                why_it_matters="Runs the fetcher.",
                installation_help_text="Install Python.",
            ),
            resolved_executable_path="/usr/bin/python",
            version_output="Python 3.12.0",
        )
        missing_requirement = RequirementStatus(
            requirement=ExternalCommandRequirement(
                display_name="Docker",
                executable_name="docker",
                why_it_matters="Optional containers.",
                installation_help_text="Install Docker.",
                is_optional=True,
            ),
            resolved_executable_path=None,
            version_output=None,
        )

        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            print_requirement_statuses([present_requirement, missing_requirement])

        rendered_output = captured_output.getvalue()
        self.assertIn("[OK] Python", rendered_output)
        self.assertIn("Python 3.12.0", rendered_output)
        self.assertIn("[OPTIONAL] Docker", rendered_output)
        self.assertIn("Install Docker.", rendered_output)

    def test_print_requirement_statuses_handles_present_tools_without_version_output(self) -> None:
        """Ensures the status report still explains a present tool when version probing is unavailable."""

        present_requirement = RequirementStatus(
            requirement=ExternalCommandRequirement(
                display_name="Python",
                executable_name="python",
                why_it_matters="Runs the fetcher.",
                installation_help_text="Install Python.",
            ),
            resolved_executable_path="/usr/bin/python",
            version_output=None,
        )

        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            print_requirement_statuses([present_requirement])

        rendered_output = captured_output.getvalue()
        self.assertIn("[OK] Python", rendered_output)
        self.assertIn("Why it matters: Runs the fetcher.", rendered_output)
        self.assertNotIn("Version:", rendered_output)

    def test_any_required_tools_are_missing_distinguishes_required_from_optional(self) -> None:
        """Ensures optional missing tools do not block the workflow."""

        optional_missing_requirement = RequirementStatus(
            requirement=ExternalCommandRequirement(
                display_name="Docker",
                executable_name="docker",
                why_it_matters="Optional containers.",
                installation_help_text="Install Docker.",
                is_optional=True,
            ),
            resolved_executable_path=None,
            version_output=None,
        )
        required_missing_requirement = RequirementStatus(
            requirement=ExternalCommandRequirement(
                display_name="Python",
                executable_name="python",
                why_it_matters="Runs the fetcher.",
                installation_help_text="Install Python.",
            ),
            resolved_executable_path=None,
            version_output=None,
        )

        self.assertFalse(any_required_tools_are_missing([optional_missing_requirement]))
        self.assertTrue(any_required_tools_are_missing([required_missing_requirement]))

    def test_any_required_tools_are_missing_returns_false_when_everything_is_present(self) -> None:
        """Ensures the doctor command can report success when all required tools exist."""

        present_requirement = RequirementStatus(
            requirement=ExternalCommandRequirement(
                display_name="Python",
                executable_name="python",
                why_it_matters="Runs the fetcher.",
                installation_help_text="Install Python.",
            ),
            resolved_executable_path="/usr/bin/python",
            version_output="Python 3.12.0",
        )

        self.assertFalse(any_required_tools_are_missing([present_requirement]))

    def test_ensure_artifact_directories_exist_creates_all_expected_directories(self) -> None:
        """Ensures the helper creates every directory the beginner flow expects."""

        with tempfile.TemporaryDirectory() as temporary_directory:
            repository_root_directory = Path(temporary_directory)

            ensure_artifact_directories_exist(repository_root_directory)

            self.assertTrue((repository_root_directory / "artifacts" / "generated").is_dir())
            self.assertTrue((repository_root_directory / "artifacts" / "logs").is_dir())
            self.assertTrue((repository_root_directory / "build" / "doxygen").is_dir())

    def test_run_execution_steps_runs_each_step_in_order(self) -> None:
        """Ensures the generic executor forwards commands, cwd, and environment to subprocess."""

        execution_steps = [
            ExecutionStep(
                step_name="first",
                command_words=("echo", "one"),
                working_directory=self.repository_root_directory,
            ),
            ExecutionStep(
                step_name="second",
                command_words=("echo", "two"),
                working_directory=self.repository_root_directory / "frontend",
            ),
        ]

        with patch("new_england_weather_data_fetcher.beginner_workflow.subprocess.run") as subprocess_run:
            run_execution_steps(execution_steps, additional_environment_variables={"UMBONI_MODE": "test"})

        self.assertEqual(2, subprocess_run.call_count)
        first_call = subprocess_run.call_args_list[0]
        second_call = subprocess_run.call_args_list[1]
        self.assertEqual(("echo", "one"), first_call.args[0])
        self.assertEqual(self.repository_root_directory, first_call.kwargs["cwd"])
        self.assertEqual("test", first_call.kwargs["env"]["UMBONI_MODE"])
        self.assertEqual(("echo", "two"), second_call.args[0])
        self.assertEqual(self.repository_root_directory / "frontend", second_call.kwargs["cwd"])

    def test_run_execution_steps_uses_an_empty_override_mapping_by_default(self) -> None:
        """Ensures the executor can run even when no extra environment variables are supplied."""

        execution_steps = [
            ExecutionStep(
                step_name="single",
                command_words=("echo", "one"),
                working_directory=self.repository_root_directory,
            )
        ]

        with patch("new_england_weather_data_fetcher.beginner_workflow.subprocess.run") as subprocess_run:
            run_execution_steps(execution_steps)

        self.assertIn("PATH", subprocess_run.call_args.kwargs["env"])

    def test_build_bootstrap_steps_returns_all_expected_steps(self) -> None:
        """Ensures the bootstrap plan covers Python and both Node workspaces."""

        bootstrap_steps = build_bootstrap_steps(self.repository_root_directory)

        self.assertEqual(4, len(bootstrap_steps))
        self.assertEqual("Create common artifact directories", bootstrap_steps[0].step_name)
        self.assertEqual(("npm", "ci"), bootstrap_steps[2].command_words)
        self.assertEqual(self.repository_root_directory / "frontend", bootstrap_steps[3].working_directory)

    def test_build_fortran_build_steps_returns_configure_and_build_steps(self) -> None:
        """Ensures the Fortran build plan contains both preset commands."""

        fortran_build_steps = build_fortran_build_steps(self.repository_root_directory)

        self.assertEqual(("cmake", "--preset", "default"), fortran_build_steps[0].command_words)
        self.assertEqual(("cmake", "--build", "--preset", "default"), fortran_build_steps[1].command_words)

    def test_build_fortran_test_steps_include_ctest_after_the_build(self) -> None:
        """Ensures the native test plan builds first and then runs CTest."""

        fortran_test_steps = build_fortran_test_steps(self.repository_root_directory)

        self.assertEqual(("cmake", "--preset", "default"), fortran_test_steps[0].command_words)
        self.assertEqual(("cmake", "--build", "--preset", "default"), fortran_test_steps[1].command_words)
        self.assertEqual(("ctest", "--preset", "default", "--output-on-failure"), fortran_test_steps[2].command_words)

    def test_pipeline_steps_fetch_then_simulate_then_sync(self) -> None:
        """Ensures the one-command pipeline runs the major stages in the expected order."""

        pipeline_steps = build_pipeline_steps(
            repository_root_directory=self.repository_root_directory,
            output_csv_path="artifacts/generated/provider-observations.csv",
            python_log_file_path="artifacts/logs/python-fetcher.log.jsonl",
            simulator_log_file_path="artifacts/logs/fortran-simulator.log.jsonl",
            maximum_hours=24,
        )

        self.assertEqual("Fetch provider data for the New England catalog", pipeline_steps[0].step_name)
        self.assertIn("--maximum-hours", pipeline_steps[0].command_words)
        self.assertEqual("Run the Fortran simulator against the normalized provider CSV", pipeline_steps[3].step_name)
        self.assertIn("--skip-fetch", pipeline_steps[3].command_words)
        self.assertEqual(
            "Copy the newest forecast JSON into the Angular public data folder",
            pipeline_steps[4].step_name,
        )

    def test_build_repository_and_python_test_steps_return_expected_commands(self) -> None:
        """Ensures the repository and Python test plans are discoverable and correct."""

        repository_test_steps = build_repository_test_steps(self.repository_root_directory)
        python_test_steps = build_python_test_steps(self.repository_root_directory)

        self.assertEqual(("npm", "run", "validate:repository"), repository_test_steps[0].command_words)
        self.assertEqual(
            (sys.executable, "-m", "unittest", "discover", "-s", "python/tests", "-t", "python"),
            python_test_steps[0].command_words,
        )

    def test_build_documentation_steps_supports_build_and_serve_modes(self) -> None:
        """Ensures the docs plan can either build static files or start a local server."""

        documentation_build_steps = build_documentation_steps(self.repository_root_directory, serve_documentation=False)
        documentation_serve_steps = build_documentation_steps(self.repository_root_directory, serve_documentation=True)

        self.assertEqual(("mkdocs", "build", "--strict"), documentation_build_steps[-1].command_words)
        self.assertEqual(("mkdocs", "serve", "--dev-addr", "127.0.0.1:8000"), documentation_serve_steps[-1].command_words)

    def test_frontend_test_steps_include_playwright_install_when_end_to_end_tests_are_enabled(self) -> None:
        """Ensures the full frontend suite includes the browser installation step."""

        frontend_test_steps = build_frontend_test_steps(
            repository_root_directory=self.repository_root_directory,
            include_end_to_end_tests=True,
        )

        self.assertEqual(
            "Install the Chromium browser used by the Playwright smoke tests",
            frontend_test_steps[4].step_name,
        )
        self.assertEqual(("npx", "playwright", "install", "chromium"), frontend_test_steps[4].command_words)
        self.assertEqual("Run the Playwright end-to-end smoke tests", frontend_test_steps[5].step_name)

    def test_frontend_test_steps_can_skip_end_to_end_tests(self) -> None:
        """Ensures users can run the lighter frontend validation path on constrained machines."""

        frontend_test_steps = build_frontend_test_steps(
            repository_root_directory=self.repository_root_directory,
            include_end_to_end_tests=False,
        )

        self.assertEqual(4, len(frontend_test_steps))
        self.assertEqual("Build the Angular dashboard", frontend_test_steps[-1].step_name)

    def test_simulation_steps_use_existing_csv_input(self) -> None:
        """Ensures the simulate command uses the explicit CSV and JSON paths it receives."""

        with patch("new_england_weather_data_fetcher.beginner_workflow.os.name", "posix"):
            simulation_steps = build_simulation_steps(
                repository_root_directory=self.repository_root_directory,
                input_csv_path="artifacts/generated/provider-observations.csv",
                output_json_path="artifacts/generated/new-england-forecast.json",
                log_file_path="artifacts/logs/fortran-simulator.log.jsonl",
            )

        simulator_command_words = simulation_steps[2].command_words
        self.assertIn("--input-csv", simulator_command_words)
        self.assertIn("artifacts/generated/provider-observations.csv", simulator_command_words)
        self.assertIn("--output-json", simulator_command_words)
        self.assertIn("artifacts/generated/new-england-forecast.json", simulator_command_words)

    def test_run_doctor_command_returns_failure_when_required_tools_are_missing(self) -> None:
        """Ensures the doctor command stops the beginner when required tools are absent."""

        requirement_statuses = [
            RequirementStatus(
                requirement=ExternalCommandRequirement(
                    display_name="Python",
                    executable_name="python",
                    why_it_matters="Runs the fetcher.",
                    installation_help_text="Install Python.",
                ),
                resolved_executable_path=None,
                version_output=None,
            )
        ]

        with patch(
            "new_england_weather_data_fetcher.beginner_workflow.collect_requirement_statuses",
            return_value=requirement_statuses,
        ), patch("new_england_weather_data_fetcher.beginner_workflow.print_requirement_statuses"):
            result = run_doctor_command()

        self.assertEqual(1, result)

    def test_run_doctor_command_returns_success_when_required_tools_are_present(self) -> None:
        """Ensures the doctor command points a healthy setup toward bootstrap."""

        requirement_statuses = [
            RequirementStatus(
                requirement=ExternalCommandRequirement(
                    display_name="Python",
                    executable_name="python",
                    why_it_matters="Runs the fetcher.",
                    installation_help_text="Install Python.",
                ),
                resolved_executable_path="/usr/bin/python",
                version_output="Python 3.12.0",
            )
        ]

        with patch(
            "new_england_weather_data_fetcher.beginner_workflow.collect_requirement_statuses",
            return_value=requirement_statuses,
        ), patch("new_england_weather_data_fetcher.beginner_workflow.print_requirement_statuses"):
            result = run_doctor_command()

        self.assertEqual(0, result)

    def test_run_bootstrap_command_prepares_directories_and_runs_steps(self) -> None:
        """Ensures bootstrap creates directories before executing the install plan."""

        with patch("new_england_weather_data_fetcher.beginner_workflow.ensure_artifact_directories_exist") as ensure_dirs, patch(
            "new_england_weather_data_fetcher.beginner_workflow.run_execution_steps"
        ) as run_steps:
            result = run_bootstrap_command(self.repository_root_directory)

        ensure_dirs.assert_called_once_with(self.repository_root_directory)
        run_steps.assert_called_once()
        self.assertEqual(0, result)

    def test_run_fetch_command_builds_and_executes_the_fetch_step(self) -> None:
        """Ensures the fetch command forwards its explicit arguments to the fetch script."""

        parsed_arguments = Namespace(
            output_csv="output.csv",
            log_file="fetch.log",
            maximum_hours=12,
        )

        with patch("new_england_weather_data_fetcher.beginner_workflow.ensure_artifact_directories_exist"), patch(
            "new_england_weather_data_fetcher.beginner_workflow.run_execution_steps"
        ) as run_steps:
            result = run_fetch_command(parsed_arguments, self.repository_root_directory)

        fetch_step = run_steps.call_args.args[0][0]
        self.assertEqual("output.csv", fetch_step.command_words[3])
        self.assertEqual("fetch.log", fetch_step.command_words[5])
        self.assertEqual("12", fetch_step.command_words[7])
        self.assertEqual(0, result)

    def test_run_build_fortran_command_executes_the_fortran_build_plan(self) -> None:
        """Ensures the dedicated Fortran build command delegates to the build-step plan."""

        with patch("new_england_weather_data_fetcher.beginner_workflow.ensure_artifact_directories_exist"), patch(
            "new_england_weather_data_fetcher.beginner_workflow.run_execution_steps"
        ) as run_steps, patch(
            "new_england_weather_data_fetcher.beginner_workflow.build_fortran_build_steps",
            return_value=[ExecutionStep("step", ("echo", "hello"), self.repository_root_directory)],
        ):
            result = run_build_fortran_command(self.repository_root_directory)

        run_steps.assert_called_once()
        self.assertEqual(0, result)

    def test_run_simulate_command_executes_the_simulation_plan(self) -> None:
        """Ensures the simulate command delegates to the simulation-step builder."""

        parsed_arguments = Namespace(
            input_csv="input.csv",
            output_json="output.json",
            log_file="simulate.log",
        )

        with patch("new_england_weather_data_fetcher.beginner_workflow.ensure_artifact_directories_exist"), patch(
            "new_england_weather_data_fetcher.beginner_workflow.run_execution_steps"
        ) as run_steps, patch(
            "new_england_weather_data_fetcher.beginner_workflow.build_simulation_steps",
            return_value=[ExecutionStep("step", ("echo", "simulate"), self.repository_root_directory)],
        ) as build_steps:
            result = run_simulate_command(parsed_arguments, self.repository_root_directory)

        build_steps.assert_called_once_with(
            repository_root_directory=self.repository_root_directory,
            input_csv_path="input.csv",
            output_json_path="output.json",
            log_file_path="simulate.log",
        )
        run_steps.assert_called_once()
        self.assertEqual(0, result)

    def test_run_pipeline_command_executes_the_pipeline_plan(self) -> None:
        """Ensures the one-command pipeline delegates to the pipeline-step builder."""

        parsed_arguments = Namespace(
            output_csv="provider.csv",
            python_log_file="python.log",
            simulator_log_file="fortran.log",
            maximum_hours=36,
        )

        with patch("new_england_weather_data_fetcher.beginner_workflow.ensure_artifact_directories_exist"), patch(
            "new_england_weather_data_fetcher.beginner_workflow.run_execution_steps"
        ) as run_steps, patch(
            "new_england_weather_data_fetcher.beginner_workflow.build_pipeline_steps",
            return_value=[ExecutionStep("step", ("echo", "pipeline"), self.repository_root_directory)],
        ) as build_steps:
            result = run_pipeline_command(parsed_arguments, self.repository_root_directory)

        build_steps.assert_called_once_with(
            repository_root_directory=self.repository_root_directory,
            output_csv_path="provider.csv",
            python_log_file_path="python.log",
            simulator_log_file_path="fortran.log",
            maximum_hours=36,
        )
        run_steps.assert_called_once()
        self.assertEqual(0, result)

    def test_run_frontend_command_executes_the_frontend_server_step(self) -> None:
        """Ensures the frontend server command uses the requested host and port."""

        parsed_arguments = Namespace(host="0.0.0.0", port=4300)

        with patch("new_england_weather_data_fetcher.beginner_workflow.run_execution_steps") as run_steps:
            result = run_frontend_command(parsed_arguments, self.repository_root_directory)

        frontend_step = run_steps.call_args.args[0][0]
        self.assertEqual(
            ("npm", "run", "start", "--", "--host", "0.0.0.0", "--port", "4300"),
            frontend_step.command_words,
        )
        self.assertEqual(self.repository_root_directory / "frontend", frontend_step.working_directory)
        self.assertEqual(0, result)

    def test_run_test_command_builds_the_requested_scope(self) -> None:
        """Ensures the test command composes the correct step list for the requested scope."""

        parsed_arguments = Namespace(
            scope="all",
            skip_end_to_end_tests=True,
            skip_documentation_build=False,
        )
        repository_steps = [ExecutionStep("repository", ("echo", "repository"), self.repository_root_directory)]
        python_steps = [ExecutionStep("python", ("echo", "python"), self.repository_root_directory)]
        fortran_steps = [ExecutionStep("fortran", ("echo", "fortran"), self.repository_root_directory)]
        frontend_steps = [ExecutionStep("frontend", ("echo", "frontend"), self.repository_root_directory)]
        documentation_steps = [ExecutionStep("docs", ("echo", "docs"), self.repository_root_directory)]

        with patch("new_england_weather_data_fetcher.beginner_workflow.ensure_artifact_directories_exist"), patch(
            "new_england_weather_data_fetcher.beginner_workflow.build_repository_test_steps",
            return_value=repository_steps,
        ), patch(
            "new_england_weather_data_fetcher.beginner_workflow.build_python_test_steps",
            return_value=python_steps,
        ), patch(
            "new_england_weather_data_fetcher.beginner_workflow.build_fortran_test_steps",
            return_value=fortran_steps,
        ), patch(
            "new_england_weather_data_fetcher.beginner_workflow.build_frontend_test_steps",
            return_value=frontend_steps,
        ) as build_frontend_steps, patch(
            "new_england_weather_data_fetcher.beginner_workflow.build_documentation_steps",
            return_value=documentation_steps,
        ), patch(
            "new_england_weather_data_fetcher.beginner_workflow.run_execution_steps"
        ) as run_steps:
            result = run_test_command(parsed_arguments, self.repository_root_directory)

        build_frontend_steps.assert_called_once_with(
            repository_root_directory=self.repository_root_directory,
            include_end_to_end_tests=False,
        )
        self.assertEqual(
            repository_steps + python_steps + fortran_steps + frontend_steps + documentation_steps,
            run_steps.call_args.args[0],
        )
        self.assertEqual(0, result)

    def test_run_test_command_can_skip_documentation_for_the_docs_scope(self) -> None:
        """Ensures documentation steps are omitted when the caller explicitly skips them."""

        parsed_arguments = Namespace(
            scope="docs",
            skip_end_to_end_tests=False,
            skip_documentation_build=True,
        )

        with patch("new_england_weather_data_fetcher.beginner_workflow.ensure_artifact_directories_exist"), patch(
            "new_england_weather_data_fetcher.beginner_workflow.run_execution_steps"
        ) as run_steps, patch(
            "new_england_weather_data_fetcher.beginner_workflow.build_documentation_steps"
        ) as build_documentation_steps:
            result = run_test_command(parsed_arguments, self.repository_root_directory)

        build_documentation_steps.assert_not_called()
        self.assertEqual([], run_steps.call_args.args[0])
        self.assertEqual(0, result)

    def test_run_build_docs_command_executes_the_documentation_build_plan(self) -> None:
        """Ensures the build-docs command delegates to the static-site plan."""

        documentation_steps = [ExecutionStep("docs", ("echo", "docs"), self.repository_root_directory)]

        with patch("new_england_weather_data_fetcher.beginner_workflow.ensure_artifact_directories_exist") as ensure_dirs, patch(
            "new_england_weather_data_fetcher.beginner_workflow.build_documentation_steps",
            return_value=documentation_steps,
        ) as build_steps, patch(
            "new_england_weather_data_fetcher.beginner_workflow.run_execution_steps"
        ) as run_steps:
            result = run_build_docs_command(self.repository_root_directory)

        ensure_dirs.assert_called_once_with(self.repository_root_directory)
        build_steps.assert_called_once_with(self.repository_root_directory, serve_documentation=False)
        run_steps.assert_called_once_with(documentation_steps)
        self.assertEqual(0, result)

    def test_run_serve_docs_command_executes_the_documentation_serve_plan(self) -> None:
        """Ensures the serve-docs command delegates to the live-server plan."""

        documentation_steps = [ExecutionStep("serve", ("echo", "serve"), self.repository_root_directory)]

        with patch("new_england_weather_data_fetcher.beginner_workflow.ensure_artifact_directories_exist") as ensure_dirs, patch(
            "new_england_weather_data_fetcher.beginner_workflow.build_documentation_steps",
            return_value=documentation_steps,
        ) as build_steps, patch(
            "new_england_weather_data_fetcher.beginner_workflow.run_execution_steps"
        ) as run_steps:
            result = run_serve_docs_command(self.repository_root_directory)

        ensure_dirs.assert_called_once_with(self.repository_root_directory)
        build_steps.assert_called_once_with(self.repository_root_directory, serve_documentation=True)
        run_steps.assert_called_once_with(documentation_steps)
        self.assertEqual(0, result)

    def test_argument_parser_accepts_beginner_commands(self) -> None:
        """Ensures the CLI parser recognizes the documented beginner commands."""

        argument_parser = build_argument_parser()

        fetch_arguments = argument_parser.parse_args(["fetch", "--output-csv", "weather.csv", "--maximum-hours", "12"])
        frontend_arguments = argument_parser.parse_args(["run-frontend", "--host", "0.0.0.0", "--port", "4300"])
        test_arguments = argument_parser.parse_args(["test", "all", "--skip-end-to-end-tests", "--skip-documentation-build"])

        self.assertEqual("fetch", fetch_arguments.command_name)
        self.assertEqual("weather.csv", fetch_arguments.output_csv)
        self.assertEqual(12, fetch_arguments.maximum_hours)
        self.assertEqual("run-frontend", frontend_arguments.command_name)
        self.assertEqual("0.0.0.0", frontend_arguments.host)
        self.assertEqual(4300, frontend_arguments.port)
        self.assertEqual("test", test_arguments.command_name)
        self.assertTrue(test_arguments.skip_end_to_end_tests)
        self.assertTrue(test_arguments.skip_documentation_build)

    def test_main_dispatches_supported_commands(self) -> None:
        """Ensures the top-level entry point routes each command to the correct helper."""

        command_scenarios = [
            ("doctor", {}, "run_doctor_command", ()),
            ("bootstrap", {}, "run_bootstrap_command", (self.repository_root_directory,)),
            ("build-fortran", {}, "run_build_fortran_command", (self.repository_root_directory,)),
            (
                "fetch",
                {"output_csv": "provider.csv", "log_file": "fetch.log", "maximum_hours": 24},
                "run_fetch_command",
                (None, self.repository_root_directory),
            ),
            (
                "simulate",
                {"input_csv": "provider.csv", "output_json": "forecast.json", "log_file": "simulate.log"},
                "run_simulate_command",
                (None, self.repository_root_directory),
            ),
            (
                "pipeline",
                {
                    "output_csv": "provider.csv",
                    "python_log_file": "python.log",
                    "simulator_log_file": "simulate.log",
                    "maximum_hours": 24,
                },
                "run_pipeline_command",
                (None, self.repository_root_directory),
            ),
            ("run-frontend", {"host": "127.0.0.1", "port": 4200}, "run_frontend_command", (None, self.repository_root_directory)),
            (
                "test",
                {"scope": "all", "skip_end_to_end_tests": False, "skip_documentation_build": False},
                "run_test_command",
                (None, self.repository_root_directory),
            ),
            ("build-docs", {}, "run_build_docs_command", (self.repository_root_directory,)),
            ("serve-docs", {}, "run_serve_docs_command", (self.repository_root_directory,)),
        ]

        for command_name, extra_fields, handler_name, expected_tail_arguments in command_scenarios:
            parsed_arguments = Namespace(command_name=command_name, **extra_fields)
            mock_parser = MagicMock()
            mock_parser.parse_args.return_value = parsed_arguments

            with self.subTest(command_name=command_name), patch(
                "new_england_weather_data_fetcher.beginner_workflow.determine_repository_root",
                return_value=self.repository_root_directory,
            ), patch(
                "new_england_weather_data_fetcher.beginner_workflow.build_argument_parser",
                return_value=mock_parser,
            ), patch(
                "new_england_weather_data_fetcher.beginner_workflow.run_doctor_command",
                return_value=11,
            ) as run_doctor, patch(
                "new_england_weather_data_fetcher.beginner_workflow.run_bootstrap_command",
                return_value=12,
            ) as run_bootstrap, patch(
                "new_england_weather_data_fetcher.beginner_workflow.run_build_fortran_command",
                return_value=13,
            ) as run_build_fortran, patch(
                "new_england_weather_data_fetcher.beginner_workflow.run_fetch_command",
                return_value=14,
            ) as run_fetch, patch(
                "new_england_weather_data_fetcher.beginner_workflow.run_simulate_command",
                return_value=15,
            ) as run_simulate, patch(
                "new_england_weather_data_fetcher.beginner_workflow.run_pipeline_command",
                return_value=16,
            ) as run_pipeline, patch(
                "new_england_weather_data_fetcher.beginner_workflow.run_frontend_command",
                return_value=17,
            ) as run_frontend, patch(
                "new_england_weather_data_fetcher.beginner_workflow.run_test_command",
                return_value=18,
            ) as run_test, patch(
                "new_england_weather_data_fetcher.beginner_workflow.run_build_docs_command",
                return_value=19,
            ) as run_build_docs, patch(
                "new_england_weather_data_fetcher.beginner_workflow.run_serve_docs_command",
                return_value=20,
            ) as run_serve_docs:
                result = main()

            handler_map = {
                "run_doctor_command": (run_doctor, 11),
                "run_bootstrap_command": (run_bootstrap, 12),
                "run_build_fortran_command": (run_build_fortran, 13),
                "run_fetch_command": (run_fetch, 14),
                "run_simulate_command": (run_simulate, 15),
                "run_pipeline_command": (run_pipeline, 16),
                "run_frontend_command": (run_frontend, 17),
                "run_test_command": (run_test, 18),
                "run_build_docs_command": (run_build_docs, 19),
                "run_serve_docs_command": (run_serve_docs, 20),
            }

            selected_handler, expected_result = handler_map[handler_name]
            expected_arguments = expected_tail_arguments
            if expected_tail_arguments and expected_tail_arguments[0] is None:
                expected_arguments = (parsed_arguments, *expected_tail_arguments[1:])
            selected_handler.assert_called_once_with(*expected_arguments)
            self.assertEqual(expected_result, result)

    def test_main_raises_for_an_unknown_command(self) -> None:
        """Ensures unsupported commands still fail loudly instead of silently doing nothing."""

        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = Namespace(command_name="unknown")

        with patch(
            "new_england_weather_data_fetcher.beginner_workflow.determine_repository_root",
            return_value=self.repository_root_directory,
        ), patch(
            "new_england_weather_data_fetcher.beginner_workflow.build_argument_parser",
            return_value=mock_parser,
        ), self.assertRaisesRegex(ValueError, "Unsupported command: unknown"):
            main()


if __name__ == "__main__":
    unittest.main()
