from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ResultCode(str, Enum):
    DONE = "done"
    HOLD = "hold"
    GRADE_POSTED = "grade_posted"
    DROP_CLOSED = "drop_closed"
    NOT_ENROLLED = "not_enrolled"
    PREREQUISITES = "prerequisites"
    CREDIT_LIMIT = "credit_limit"
    WAITLISTED = "waitlisted"
    ALREADY_ENROLLED = "already_enrolled"
    ADD_CLOSED = "add_closed"
    DATABASE_ERROR = "database_error"
    INVALID_ARGUMENTS = "invalid_arguments"


@dataclass(frozen=True)
class OperationResult:
    code: ResultCode
    message: str
    exit_code: int


RESULTS: dict[ResultCode, OperationResult] = {
    ResultCode.DONE: OperationResult(ResultCode.DONE, "Done.", 0),
    ResultCode.HOLD: OperationResult(
        ResultCode.HOLD,
        "Cannot proceed: student has a registration hold.",
        1,
    ),
    ResultCode.GRADE_POSTED: OperationResult(
        ResultCode.GRADE_POSTED,
        "Cannot drop: a grade has already been posted.",
        1,
    ),
    ResultCode.DROP_CLOSED: OperationResult(
        ResultCode.DROP_CLOSED,
        "Cannot drop: the drop deadline has passed.",
        1,
    ),
    ResultCode.NOT_ENROLLED: OperationResult(
        ResultCode.NOT_ENROLLED,
        "Student is not enrolled in that section.",
        1,
    ),
    ResultCode.PREREQUISITES: OperationResult(
        ResultCode.PREREQUISITES,
        "Cannot add: prerequisites are not satisfied.",
        1,
    ),
    ResultCode.CREDIT_LIMIT: OperationResult(
        ResultCode.CREDIT_LIMIT,
        "Cannot add: credit limit exceeded.",
        1,
    ),
    ResultCode.WAITLISTED: OperationResult(
        ResultCode.WAITLISTED,
        "Section full -- student placed on the waitlist.",
        0,
    ),
    ResultCode.ALREADY_ENROLLED: OperationResult(
        ResultCode.ALREADY_ENROLLED,
        "Student is already enrolled in that section.",
        1,
    ),
    ResultCode.ADD_CLOSED: OperationResult(
        ResultCode.ADD_CLOSED,
        "Cannot add: registration for this term is closed.",
        1,
    ),
    ResultCode.DATABASE_ERROR: OperationResult(
        ResultCode.DATABASE_ERROR,
        "Database error.",
        2,
    ),
    ResultCode.INVALID_ARGUMENTS: OperationResult(
        ResultCode.INVALID_ARGUMENTS,
        "Usage: registration-port <drop|add|swap> ...",
        2,
    ),
}


def result_for(code: ResultCode) -> OperationResult:
    return RESULTS[code]
