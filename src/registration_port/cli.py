from __future__ import annotations

import argparse
import sys
from pathlib import Path

from registration_port.db import RegistrationRepository, connect
from registration_port.results import ResultCode, result_for
from registration_port.service import RegistrationService


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_PATH = PROJECT_ROOT / "registration.sqlite3"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="registration-port")
    parser.add_argument(
        "--database",
        default=str(DEFAULT_DATABASE_PATH),
        help=argparse.SUPPRESS,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("drop", "add"):
        operation_parser = subparsers.add_parser(command)
        operation_parser.add_argument("student_id", type=int)
        operation_parser.add_argument("section_code")
        operation_parser.add_argument("year", type=int)
        operation_parser.add_argument("session")

    swap_parser = subparsers.add_parser("swap")
    swap_parser.add_argument("student_id", type=int)
    swap_parser.add_argument("drop_section_code")
    swap_parser.add_argument("add_section_code")
    swap_parser.add_argument("year", type=int)
    swap_parser.add_argument("session")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as error:
        return int(error.code)

    connection = connect(args.database)
    try:
        service = RegistrationService(RegistrationRepository(connection))
        if args.command == "drop":
            result = service.do_drop(
                args.student_id,
                args.section_code,
                args.year,
                args.session,
            )
        elif args.command == "add":
            result = service.do_add(
                args.student_id,
                args.section_code,
                args.year,
                args.session,
            )
        elif args.command == "swap":
            result = service.do_swap(
                args.student_id,
                args.drop_section_code,
                args.add_section_code,
                args.year,
                args.session,
            )
        else:
            result = result_for(ResultCode.INVALID_ARGUMENTS)
    finally:
        connection.close()

    print(result.message)
    return result.exit_code


if __name__ == "__main__":
    sys.exit(main())
