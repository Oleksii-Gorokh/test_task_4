from __future__ import annotations

import pytest

from registration_port.cli import main


@pytest.mark.parametrize(
    ("arguments", "message", "exit_code"),
    [
        (["drop", "1001", "CS101-01", "2024", "S"], "Done.", 0),
        (["drop", "1002", "CS101-02", "2024", "S"], "Done.", 0),
        (
            ["drop", "1003", "CS101-01", "2024", "S"],
            "Cannot proceed: student has a registration hold.",
            1,
        ),
        (
            ["drop", "1004", "CS101-01", "2024", "S"],
            "Cannot drop: a grade has already been posted.",
            1,
        ),
        (
            ["drop", "1001", "HX999-01", "2023", "F"],
            "Cannot drop: the drop deadline has passed.",
            1,
        ),
        (
            ["drop", "1007", "CS101-02", "2024", "S"],
            "Student is not enrolled in that section.",
            1,
        ),
        (["add", "1007", "CS101-02", "2024", "S"], "Done.", 0),
        (
            ["add", "1007", "CS201-01", "2024", "S"],
            "Cannot add: prerequisites are not satisfied.",
            1,
        ),
        (
            ["add", "1007", "PHIL300-1", "2024", "S"],
            "Cannot add: prerequisites are not satisfied.",
            1,
        ),
        (
            ["add", "1008", "PHIL300-1", "2024", "S"],
            "Section full -- student placed on the waitlist.",
            0,
        ),
        (
            ["add", "1001", "MA200-01", "2024", "S"],
            "Student is already enrolled in that section.",
            1,
        ),
        (
            ["add", "1007", "HX999-01", "2023", "F"],
            "Cannot add: registration for this term is closed.",
            1,
        ),
        (
            ["add", "1007", "CS101-01", "2024", "S"],
            "Section full -- student placed on the waitlist.",
            0,
        ),
        (["swap", "1001", "CS101-01", "CS201-01", "2024", "S"], "Done.", 0),
        (
            ["swap", "1001", "MA200-01", "CS999-01", "2024", "S"],
            "Student is not enrolled in that section.",
            1,
        ),
    ],
)
def test_acceptance_scenarios(
    database_path,
    capsys: pytest.CaptureFixture[str],
    arguments: list[str],
    message: str,
    exit_code: int,
) -> None:
    result = main(["--database", str(database_path), *arguments])

    captured = capsys.readouterr()
    assert result == exit_code
    assert captured.out == f"{message}\n"
