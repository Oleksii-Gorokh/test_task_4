PRAGMA foreign_keys = ON;

CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    max_credits INTEGER NOT NULL DEFAULT 18 CHECK (max_credits >= 0),
    has_registration_hold INTEGER NOT NULL DEFAULT 0 CHECK (has_registration_hold IN (0, 1))
);

CREATE TABLE terms (
    year INTEGER NOT NULL,
    session TEXT NOT NULL,
    add_open INTEGER NOT NULL CHECK (add_open IN (0, 1)),
    drop_open INTEGER NOT NULL CHECK (drop_open IN (0, 1)),
    PRIMARY KEY (year, session)
);

CREATE TABLE sections (
    code TEXT NOT NULL,
    year INTEGER NOT NULL,
    session TEXT NOT NULL,
    course_code TEXT NOT NULL,
    credits INTEGER NOT NULL CHECK (credits > 0),
    capacity INTEGER NOT NULL CHECK (capacity >= 0),
    PRIMARY KEY (code, year, session),
    FOREIGN KEY (year, session) REFERENCES terms (year, session)
);

CREATE TABLE enrollments (
    student_id INTEGER NOT NULL,
    section_code TEXT NOT NULL,
    year INTEGER NOT NULL,
    session TEXT NOT NULL,
    grade TEXT,
    PRIMARY KEY (student_id, section_code, year, session),
    FOREIGN KEY (student_id) REFERENCES students (id),
    FOREIGN KEY (section_code, year, session) REFERENCES sections (code, year, session)
);

CREATE TABLE completed_courses (
    student_id INTEGER NOT NULL,
    course_code TEXT NOT NULL,
    PRIMARY KEY (student_id, course_code),
    FOREIGN KEY (student_id) REFERENCES students (id)
);

CREATE TABLE course_prerequisites (
    course_code TEXT NOT NULL,
    prerequisite_course_code TEXT NOT NULL,
    PRIMARY KEY (course_code, prerequisite_course_code)
);

CREATE TABLE waitlist (
    student_id INTEGER NOT NULL,
    section_code TEXT NOT NULL,
    year INTEGER NOT NULL,
    session TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, section_code, year, session),
    FOREIGN KEY (student_id) REFERENCES students (id),
    FOREIGN KEY (section_code, year, session) REFERENCES sections (code, year, session)
);
