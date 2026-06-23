from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Student:
    id: int
    max_credits: int
    has_registration_hold: bool


@dataclass(frozen=True)
class Term:
    add_open: bool
    drop_open: bool


@dataclass(frozen=True)
class Section:
    code: str
    year: int
    session: str
    course_code: str
    credits: int
    capacity: int


@dataclass(frozen=True)
class Enrollment:
    student_id: int
    section_code: str
    year: int
    session: str
    grade: str | None


class RegistrationRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

    @contextmanager
    def transaction(self) -> Iterator[None]:
        try:
            self.connection.execute("BEGIN")
            yield
        except Exception:
            self.connection.rollback()
            raise
        else:
            self.connection.commit()

    def get_student(self, student_id: int) -> Student | None:
        row = self.connection.execute(
            "SELECT id, max_credits, has_registration_hold FROM students WHERE id = ?",
            (student_id,),
        ).fetchone()
        if row is None:
            return None
        return Student(
            id=row["id"],
            max_credits=row["max_credits"],
            has_registration_hold=bool(row["has_registration_hold"]),
        )

    def get_term(self, year: int, session: str) -> Term | None:
        row = self.connection.execute(
            "SELECT add_open, drop_open FROM terms WHERE year = ? AND session = ?",
            (year, session),
        ).fetchone()
        if row is None:
            return None
        return Term(add_open=bool(row["add_open"]), drop_open=bool(row["drop_open"]))

    def get_section(self, section_code: str, year: int, session: str) -> Section | None:
        row = self.connection.execute(
            """
            SELECT code, year, session, course_code, credits, capacity
            FROM sections
            WHERE code = ? AND year = ? AND session = ?
            """,
            (section_code, year, session),
        ).fetchone()
        if row is None:
            return None
        return Section(
            code=row["code"],
            year=row["year"],
            session=row["session"],
            course_code=row["course_code"],
            credits=row["credits"],
            capacity=row["capacity"],
        )

    def get_enrollment(
        self,
        student_id: int,
        section_code: str,
        year: int,
        session: str,
    ) -> Enrollment | None:
        row = self.connection.execute(
            """
            SELECT student_id, section_code, year, session, grade
            FROM enrollments
            WHERE student_id = ? AND section_code = ? AND year = ? AND session = ?
            """,
            (student_id, section_code, year, session),
        ).fetchone()
        if row is None:
            return None
        return Enrollment(
            student_id=row["student_id"],
            section_code=row["section_code"],
            year=row["year"],
            session=row["session"],
            grade=row["grade"],
        )

    def count_enrollments(self, section_code: str, year: int, session: str) -> int:
        row = self.connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM enrollments
            WHERE section_code = ? AND year = ? AND session = ?
            """,
            (section_code, year, session),
        ).fetchone()
        return int(row["count"])

    def count_missing_prerequisites(self, student_id: int, course_code: str) -> int:
        row = self.connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM course_prerequisites AS prerequisite
            WHERE prerequisite.course_code = ?
              AND NOT EXISTS (
                  SELECT 1
                  FROM completed_courses AS completed
                  WHERE completed.student_id = ?
                    AND completed.course_code = prerequisite.prerequisite_course_code
              )
            """,
            (course_code, student_id),
        ).fetchone()
        return int(row["count"])

    def sum_enrolled_credits(self, student_id: int, year: int, session: str) -> int:
        row = self.connection.execute(
            """
            SELECT COALESCE(SUM(section.credits), 0) AS credits
            FROM enrollments AS enrollment
            JOIN sections AS section
              ON section.code = enrollment.section_code
             AND section.year = enrollment.year
             AND section.session = enrollment.session
            WHERE enrollment.student_id = ?
              AND enrollment.year = ?
              AND enrollment.session = ?
            """,
            (student_id, year, session),
        ).fetchone()
        return int(row["credits"])

    def delete_enrollment(
        self,
        student_id: int,
        section_code: str,
        year: int,
        session: str,
    ) -> None:
        self.connection.execute(
            """
            DELETE FROM enrollments
            WHERE student_id = ? AND section_code = ? AND year = ? AND session = ?
            """,
            (student_id, section_code, year, session),
        )

    def add_enrollment(
        self,
        student_id: int,
        section_code: str,
        year: int,
        session: str,
    ) -> None:
        self.connection.execute(
            """
            INSERT INTO enrollments (student_id, section_code, year, session, grade)
            VALUES (?, ?, ?, ?, NULL)
            """,
            (student_id, section_code, year, session),
        )

    def add_to_waitlist(
        self,
        student_id: int,
        section_code: str,
        year: int,
        session: str,
    ) -> None:
        self.connection.execute(
            """
            INSERT OR IGNORE INTO waitlist (student_id, section_code, year, session)
            VALUES (?, ?, ?, ?)
            """,
            (student_id, section_code, year, session),
        )


def connect(database_path: str | Path) -> sqlite3.Connection:
    return sqlite3.connect(database_path)


def initialize_database(
    database_path: str | Path,
    schema_path: str | Path,
    seed_path: str | Path,
) -> None:
    connection = connect(database_path)
    try:
        connection.executescript(Path(schema_path).read_text(encoding="utf-8"))
        connection.executescript(Path(seed_path).read_text(encoding="utf-8"))
        connection.commit()
    finally:
        connection.close()
