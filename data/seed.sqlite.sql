INSERT INTO students (id, full_name, max_credits, has_registration_hold) VALUES
    (1001, 'Alex Morgan', 18, 0),
    (1002, 'Blair Chen', 18, 0),
    (1003, 'Casey Patel', 18, 1),
    (1004, 'Dana Kovalenko', 18, 0),
    (1005, 'Evan Torres', 18, 0),
    (1007, 'Finn Novak', 18, 0),
    (1008, 'Gia Evans', 18, 0),
    (1009, 'Harper Lee', 18, 0);

INSERT INTO terms (year, session, add_open, drop_open) VALUES
    (2024, 'S', 1, 1),
    (2023, 'F', 0, 0);

INSERT INTO sections (code, year, session, course_code, credits, capacity) VALUES
    ('CS101-01', 2024, 'S', 'CS101', 3, 3),
    ('CS101-02', 2024, 'S', 'CS101', 3, 2),
    ('CS201-01', 2024, 'S', 'CS201', 3, 3),
    ('MA200-01', 2024, 'S', 'MA200', 4, 3),
    ('PHIL300-1', 2024, 'S', 'PHIL300', 3, 1),
    ('HX999-01', 2023, 'F', 'HX999', 3, 2);

INSERT INTO enrollments (student_id, section_code, year, session, grade) VALUES
    (1001, 'CS101-01', 2024, 'S', NULL),
    (1001, 'MA200-01', 2024, 'S', NULL),
    (1001, 'HX999-01', 2023, 'F', NULL),
    (1002, 'CS101-02', 2024, 'S', NULL),
    (1003, 'CS101-01', 2024, 'S', NULL),
    (1004, 'CS101-01', 2024, 'S', 'A'),
    (1009, 'PHIL300-1', 2024, 'S', NULL);

INSERT INTO completed_courses (student_id, course_code) VALUES
    (1001, 'CS101'),
    (1008, 'PHIL200');

INSERT INTO course_prerequisites (course_code, prerequisite_course_code) VALUES
    ('CS201', 'CS101'),
    ('PHIL300', 'PHIL200');
