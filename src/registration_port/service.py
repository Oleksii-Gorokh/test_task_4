from __future__ import annotations

import sqlite3
from collections.abc import Callable

from registration_port.db import RegistrationRepository
from registration_port.results import OperationResult, ResultCode, result_for


Operation = Callable[[], OperationResult]


class RegistrationService:
    def __init__(self, repository: RegistrationRepository) -> None:
        self.repository = repository

    def do_drop(
        self,
        student_id: int,
        section_code: str,
        year: int,
        session: str,
    ) -> OperationResult:
        return self._run_in_transaction(
            lambda: self._drop(student_id, section_code, year, session)
        )

    def do_add(
        self,
        student_id: int,
        section_code: str,
        year: int,
        session: str,
    ) -> OperationResult:
        return self._run_in_transaction(
            lambda: self._add(student_id, section_code, year, session)
        )

    def do_swap(
        self,
        student_id: int,
        drop_section_code: str,
        add_section_code: str,
        year: int,
        session: str,
    ) -> OperationResult:
        def operation() -> OperationResult:
            drop_result = self._drop(student_id, drop_section_code, year, session)
            if drop_result.code is not ResultCode.DONE:
                return drop_result
            add_result = self._add(student_id, add_section_code, year, session)
            if add_result.exit_code != 0:
                raise SwapRejected(add_result)
            return add_result

        try:
            return self._run_in_transaction(operation)
        except SwapRejected as error:
            return error.result

    def _run_in_transaction(self, operation: Operation) -> OperationResult:
        try:
            with self.repository.transaction():
                return operation()
        except sqlite3.DatabaseError:
            return result_for(ResultCode.DATABASE_ERROR)

    def _drop(
        self,
        student_id: int,
        section_code: str,
        year: int,
        session: str,
    ) -> OperationResult:
        student = self.repository.get_student(student_id)
        if student is not None and student.has_registration_hold:
            return result_for(ResultCode.HOLD)

        enrollment = self.repository.get_enrollment(student_id, section_code, year, session)
        if enrollment is None:
            return result_for(ResultCode.NOT_ENROLLED)

        if enrollment.grade is not None:
            return result_for(ResultCode.GRADE_POSTED)

        term = self.repository.get_term(year, session)
        if term is None or not term.drop_open:
            return result_for(ResultCode.DROP_CLOSED)

        self.repository.delete_enrollment(student_id, section_code, year, session)
        return result_for(ResultCode.DONE)

    def _add(
        self,
        student_id: int,
        section_code: str,
        year: int,
        session: str,
    ) -> OperationResult:
        student = self.repository.get_student(student_id)
        if student is not None and student.has_registration_hold:
            return result_for(ResultCode.HOLD)

        if self.repository.get_enrollment(student_id, section_code, year, session) is not None:
            return result_for(ResultCode.ALREADY_ENROLLED)

        term = self.repository.get_term(year, session)
        if term is None or not term.add_open:
            return result_for(ResultCode.ADD_CLOSED)

        section = self.repository.get_section(section_code, year, session)
        if section is None:
            return result_for(ResultCode.NOT_ENROLLED)

        missing_prerequisites = self.repository.count_missing_prerequisites(
            student_id,
            section.course_code,
        )
        if missing_prerequisites:
            return result_for(ResultCode.PREREQUISITES)

        current_credits = self.repository.sum_enrolled_credits(student_id, year, session)
        if student is not None and current_credits + section.credits > student.max_credits:
            return result_for(ResultCode.CREDIT_LIMIT)

        enrolled_count = self.repository.count_enrollments(section_code, year, session)
        if enrolled_count >= section.capacity:
            self.repository.add_to_waitlist(student_id, section_code, year, session)
            return result_for(ResultCode.WAITLISTED)

        self.repository.add_enrollment(student_id, section_code, year, session)
        return result_for(ResultCode.DONE)


class SwapRejected(Exception):
    def __init__(self, result: OperationResult) -> None:
        super().__init__(result.message)
        self.result = result
