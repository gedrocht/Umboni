"""Tests for the beginner-friendly repository task runner."""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from new_england_weather_data_fetcher.beginner_workflow import (
    build_argument_parser,
    build_frontend_test_steps,
    build_pipeline_steps,
    build_simulation_steps,
    determine_simulator_executable_path,
)


class BeginnerWorkflowTests(unittest.TestCase):
    """Covers the command construction used by the task runner."""

    def setUp(self) -> None:
        """Creates a stable repository-root path for command-construction tests."""

        self.repository_root_directory = Path("/umboni-repository")

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

    def test_frontend_test_steps_include_playwright_install_when_end_to_end_tests_are_enabled(self) -> None:
        """Ensures the full frontend suite includes the browser installation step."""

        frontend_test_steps = build_frontend_test_steps(
            repository_root_directory=self.repository_root_directory,
            include_end_to_end_tests=True,
        )

        self.assertEqual("Install the Chromium browser used by the Playwright smoke tests", frontend_test_steps[4].step_name)
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

    def test_argument_parser_accepts_beginner_commands(self) -> None:
        """Ensures the documented command names really exist in the parser."""

        argument_parser = build_argument_parser()
        parsed_arguments = argument_parser.parse_args(["test", "all", "--skip-end-to-end-tests"])

        self.assertEqual("test", parsed_arguments.command_name)
        self.assertEqual("all", parsed_arguments.scope)
        self.assertTrue(parsed_arguments.skip_end_to_end_tests)


if __name__ == "__main__":
    unittest.main()
