from __future__ import annotations

import sqlite3

from registration_port.db import RegistrationRepository, connect
from registration_port.results import ResultCode
from registration_port.service import RegistrationService


def test_successful_add_creates_enrollment(database_path) -> None:
    connection = connect(database_path)
    try:
        service = RegistrationService(RegistrationRepository(connection))

        result = service.do_add(1007, "CS101-02", 2024, "S")

        row = connection.execute(
            """
            SELECT 1
            FROM enrollments
            WHERE student_id = ? AND section_code = ? AND year = ? AND session = ?
            """,
            (1007, "CS101-02", 2024, "S"),
        ).fetchone()
        assert result.code is ResultCode.DONE
        assert row is not None
    finally:
        connection.close()


def test_full_section_add_creates_waitlist_entry(database_path) -> None:
    connection = connect(database_path)
    try:
        service = RegistrationService(RegistrationRepository(connection))

        result = service.do_add(1008, "PHIL300-1", 2024, "S")

        row = connection.execute(
            """
            SELECT 1
            FROM waitlist
            WHERE student_id = ? AND section_code = ? AND year = ? AND session = ?
            """,
            (1008, "PHIL300-1", 2024, "S"),
        ).fetchone()
        assert result.code is ResultCode.WAITLISTED
        assert row is not None
    finally:
        connection.close()


def test_swap_rolls_back_drop_when_add_fails(database_path) -> None:
    connection = connect(database_path)
    try:
        service = RegistrationService(RegistrationRepository(connection))

        result = service.do_swap(1001, "CS101-01", "CS999-01", 2024, "S")

        enrollment = connection.execute(
            """
            SELECT 1
            FROM enrollments
            WHERE student_id = ? AND section_code = ? AND year = ? AND session = ?
            """,
            (1001, "CS101-01", 2024, "S"),
        ).fetchone()
        assert result.code is ResultCode.NOT_ENROLLED
        assert enrollment is not None
    finally:
        connection.close()


def test_swap_commits_when_add_places_student_on_waitlist(database_path) -> None:
    connection = connect(database_path)
    try:
        connection.execute(
            """
            INSERT INTO enrollments (student_id, section_code, year, session, grade)
            VALUES (?, ?, ?, ?, NULL)
            """,
            (1008, "CS101-02", 2024, "S"),
        )
        connection.commit()
        service = RegistrationService(RegistrationRepository(connection))

        result = service.do_swap(1008, "CS101-02", "PHIL300-1", 2024, "S")

        old_enrollment = connection.execute(
            """
            SELECT 1
            FROM enrollments
            WHERE student_id = ? AND section_code = ? AND year = ? AND session = ?
            """,
            (1008, "CS101-02", 2024, "S"),
        ).fetchone()
        waitlist_entry = connection.execute(
            """
            SELECT 1
            FROM waitlist
            WHERE student_id = ? AND section_code = ? AND year = ? AND session = ?
            """,
            (1008, "PHIL300-1", 2024, "S"),
        ).fetchone()
        assert result.code is ResultCode.WAITLISTED
        assert old_enrollment is None
        assert waitlist_entry is not None
    finally:
        connection.close()


def test_database_error_rolls_back_transaction(database_path) -> None:
    connection = connect(database_path)
    repository = RegistrationRepository(connection)
    service = RegistrationService(repository)
    original_delete = repository.delete_enrollment

    def failing_delete(
        student_id: int,
        section_code: str,
        year: int,
        session: str,
    ) -> None:
        original_delete(student_id, section_code, year, session)
        raise sqlite3.OperationalError("simulated failure")

    repository.delete_enrollment = failing_delete
    try:
        result = service.do_drop(1001, "CS101-01", 2024, "S")

        enrollment = connection.execute(
            """
            SELECT 1
            FROM enrollments
            WHERE student_id = ? AND section_code = ? AND year = ? AND session = ?
            """,
            (1001, "CS101-01", 2024, "S"),
        ).fetchone()
        assert result.code is ResultCode.DATABASE_ERROR
        assert enrollment is not None
    finally:
        connection.close()


def test_credit_limit_is_checked_before_capacity(database_path) -> None:
    connection = connect(database_path)
    try:
        connection.execute("UPDATE students SET max_credits = 3 WHERE id = 1007")
        connection.execute(
            """
            INSERT INTO enrollments (student_id, section_code, year, session, grade)
            VALUES (?, ?, ?, ?, NULL)
            """,
            (1007, "CS101-02", 2024, "S"),
        )
        connection.commit()
        service = RegistrationService(RegistrationRepository(connection))

        result = service.do_add(1007, "MA200-01", 2024, "S")

        assert result.code is ResultCode.CREDIT_LIMIT
    finally:
        connection.close()
