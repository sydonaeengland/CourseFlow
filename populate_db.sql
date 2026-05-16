-- ============================================================
-- COMP3161 - Data Population Script
-- Password for all accounts: password123
-- ============================================================

USE course_management;

-- 0. Clear existing data (safe to re-run)
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE submissions;
TRUNCATE TABLE assignments;
TRUNCATE TABLE items;
TRUNCATE TABLE sections;
TRUNCATE TABLE threads;
TRUNCATE TABLE forums;
TRUNCATE TABLE calendar_events;
TRUNCATE TABLE enrollments;
TRUNCATE TABLE courses;
TRUNCATE TABLE users;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. Insert Admin
INSERT INTO users (username, password, email, fname, lname, role) VALUES
('admin', '$2b$12$m7a3gbvLiRMOXtbspJ1.v.HFbgOch5LRo3QV7siwcRRG0IND69vdi', 'admin@school.edu', 'System', 'Admin', 'admin');

-- 2. Insert 200 Lecturers
INSERT INTO users (username, password, email, fname, lname, role)
SELECT
    CONCAT('lecturer', n),
    '$2b$12$m7a3gbvLiRMOXtbspJ1.v.HFbgOch5LRo3QV7siwcRRG0IND69vdi',
    CONCAT('lecturer', n, '@school.edu'),
    ELT(1 + MOD(n, 60),
        'Akeem','Shanelle','Marlon','Latoya','Damion','Patrice','Rohan','Nadine','Delroy','Tashana',
        'Fabian','Shenique','Winston','Beverley','Clive','Kezia','Orville','Simone','Dwayne','Camille',
        'Jermaine','Tenesha','Leroy','Monique','Andre','Dionne','Carlton','Stacey','Everton','Keturah',
        'Fitzroy','Paulette','Garfield','Novelette','Courtney','Hyacinth','Donovan','Annmarie','Lancelot','Sonia',
        'Oliver','Emma','William','Charlotte','George','Amelia','Edward','Victoria','James','Florence',
        'Carlos','Isabella','Miguel','Valentina','Jean','Marie','Pierre','Sophie','Antoine','Isabelle'),
    ELT(1 + MOD(n * 3, 70),
        'Campbell','Morrison','Brown','Francis','Henry','Gordon','Reid','Grant','Thomas','Barrett',
        'Bailey','Blake','Clarke','Douglas','Edwards','Fletcher','Gibson','Hamilton','Irving','James',
        'Beckford','Chin','Wong','Chang','Lee','Burke','Stewart','McLean','McIntosh','McNab',
        'Levy','Lyn','Hylton','Scarlett','Samuels','Ricketts','Daley','Facey','Lawson','Pinnock',
        'Smith','Jones','Davies','Evans','Wilson','Taylor','Hughes','Roberts','Walker','White',
        'Garcia','Rodriguez','Fernandez','Lopez','Gonzalez','Ramirez','Sanchez','Perez','Torres','Flores',
        'Bernard','Dubois','Laurent','Martin','Moreau','Rousseau','Fontaine','Leclerc','Dupont','Garnier'),
    'lecturer'
FROM (
    SELECT a.N + b.N * 10 + c.N * 100 + 1 AS n
    FROM
        (SELECT 0 AS N UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4
         UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) a,
        (SELECT 0 AS N UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4
         UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) b,
        (SELECT 0 AS N UNION SELECT 1) c
) nums WHERE n <= 200;

-- 3. Insert 100,000 Students (set-based, no DELIMITER needed)
INSERT INTO users (username, password, email, fname, lname, role)
SELECT
    CONCAT('student', n),
    '$2b$12$m7a3gbvLiRMOXtbspJ1.v.HFbgOch5LRo3QV7siwcRRG0IND69vdi',
    CONCAT('student', n, '@school.edu'),
    ELT(1 + MOD(n, 100),
        'Jaheim','Tavia','Omari','Shanique','Kevon','Brianna','Romario','Destiny','Tajay','Kadia',
        'Dejour','Jade','Tyrese','Jada','Jovan','Danielle','Rasheem','Gabrielle','Malik','Imani',
        'Kymani','Renae','Jahvon','Kiara','Devante','Shaneka','Lemar','Chevanese','Tariq','Jasmine',
        'Omarion','Tameka','Zidane','Nadia','Kemar','Aaliyah','Kadeem','Staci','Deshawn','Petrina',
        'Javonte','Ashanti','Tremaine','Rochelle','Kimani','Oneika','Tyrell','Sasha','Mikael','Shelly',
        'Jaheem','Tanesha','Romairo','Jhanae','Tavaris','Kellisha','Devonte','Tamara','Rashaun','Kayla',
        'Omari','Zanelle','Kaylia','Tricia','Shanice','Tiffany','Zanaya','Aaliya','Zara','Tiana',
        'Javion','Briella','Romaine','Gabriella','Dejean','Daniella','Tareke','Imari','Kavon','Janae',
        'Liam','Chloe','Noah','Zoe','Ethan','Mia','Lucas','Ella','Mason','Ava',
        'Diego','Isabella','Mateo','Sofia','Carlos','Valentina','Miguel','Camila','Rafael','Lucia'),
    ELT(1 + MOD(n * 7, 90),
        'Campbell','Morrison','Brown','Francis','Henry','Gordon','Reid','Grant','Thomas','Barrett',
        'Bailey','Blake','Clarke','Douglas','Edwards','Fletcher','Gibson','Hamilton','Irving','James',
        'Beckford','Chin','Wong','Chang','Lee','Burke','Stewart','McLean','McIntosh','McNab',
        'Levy','Lyn','Hylton','Scarlett','Samuels','Ricketts','Daley','Facey','Lawson','Pinnock',
        'Bennett','Senior','Anderson','Williams','Johnson','Davis','Jackson','White','Harris','Martin',
        'Marley','Tosh','Ranglin','Dekker','Perry','Kong','Livingston','Jobson','Wilmot','Palmer',
        'Smith','Jones','Davies','Evans','Wilson','Taylor','Hughes','Roberts','Walker','Allen',
        'Garcia','Rodriguez','Fernandez','Lopez','Gonzalez','Ramirez','Sanchez','Perez','Torres','Flores',
        'Bernard','Dubois','Laurent','Moreau','Rousseau','Fontaine','Leclerc','Dupont','Garnier','Simon'),
    'student'
FROM (
    SELECT a.n + b.n * 10 + c.n * 100 + d.n * 1000 + e.n * 10000 + 1 AS n
    FROM
        (SELECT 0 AS n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4
         UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) a,
        (SELECT 0 AS n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4
         UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) b,
        (SELECT 0 AS n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4
         UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) c,
        (SELECT 0 AS n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4
         UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) d,
        (SELECT 0 AS n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4
         UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) e
) nums WHERE n <= 100000;

-- 4. Insert 200 Courses
INSERT INTO courses (ccode, cname, description, created_by, lecturerID)
SELECT
    CONCAT('CRS', LPAD(n, 3, '0')),
    CONCAT(
        ELT(1 + MOD(n, 8),
            'Introduction to ', 'Advanced ', 'Principles of ', 'Foundations of ',
            'Applied ', 'Theory of ', 'Topics in ', 'Studies in '),
        ELT(1 + MOD(n, 13),
            'Computer Science', 'Mathematics', 'Physics', 'Chemistry',
            'Biology', 'Engineering', 'Data Science', 'Networks',
            'Databases', 'Algorithms', 'Software Engineering', 'Cybersecurity',
            'Artificial Intelligence')
    ),
    CONCAT('Core course number ', n),
    1,
    2 + MOD(n - 1, 200)
FROM (
    SELECT a.N + b.N * 10 + c.N * 100 + 1 AS n
    FROM
        (SELECT 0 AS N UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4
         UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) a,
        (SELECT 0 AS N UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4
         UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) b,
        (SELECT 0 AS N UNION SELECT 1) c
) nums WHERE n <= 200;

-- 5. Redistribute lecturers so some teach 3+ courses (max 5)
UPDATE courses
SET lecturerID = 2 + MOD(courseID, 67)
WHERE courseID > 0;

-- 6. Enroll Students (3-6 courses per student, set-based, no DELIMITER needed)
INSERT IGNORE INTO enrollments (courseID, studID)
SELECT
    1 + MOD(u.userID * 7 + offsets.n * 13, 200) AS courseID,
    u.userID AS studID
FROM users u
JOIN (SELECT 0 AS n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3
      UNION SELECT 4 UNION SELECT 5) offsets
WHERE u.role = 'student'
  AND offsets.n < (3 + MOD(u.userID, 4));

-- 7. Insert Calendar Events (2 per course)
INSERT INTO calendar_events (courseID, title, description, event_date, start_time, end_time, created_by)
SELECT
    c.courseID,
    CONCAT('Lecture - Week ', MOD(c.courseID, 14) + 1),
    'Regular scheduled lecture',
    DATE_ADD('2025-01-13', INTERVAL MOD(c.courseID, 90) DAY),
    '09:00:00', '11:00:00',
    1
FROM courses c
UNION ALL
SELECT
    c.courseID,
    CONCAT('Assignment Due - ', c.ccode),
    'Assignment submission deadline',
    DATE_ADD('2025-02-01', INTERVAL MOD(c.courseID, 60) DAY),
    '23:59:00', '23:59:00',
    1
FROM courses c;

-- 8. Insert Forums (2 per course with distinct names)
INSERT INTO forums (courseID, title, created_by)
SELECT courseID, CONCAT('General Discussion'), 1
FROM courses;

INSERT INTO forums (courseID, title, created_by)
SELECT courseID, CONCAT('Questions & Help'), 1
FROM courses;

-- 9. Insert Discussion Threads (2 per forum)
INSERT INTO threads (forumID, title, body, created_by)
SELECT f.forumID,
    'Welcome to the course!',
    'Please introduce yourself and share your expectations for this course.',
    1
FROM forums f
UNION ALL
SELECT f.forumID,
    'Questions and Answers',
    'Use this thread to ask any course-related questions.',
    1
FROM forums f;

-- 10. Insert Sections (2 per course)
INSERT INTO sections (courseID, title, position)
SELECT courseID, CONCAT('Week 1 - ', ccode), 1 FROM courses
UNION ALL
SELECT courseID, CONCAT('Week 2 - ', ccode), 2 FROM courses;

-- 11. Insert Items (2 per section)
INSERT INTO items (sectionID, type, title, url, uploaded_by)
SELECT s.sectionID, 'link', CONCAT('Lecture Notes - ', s.title),
       CONCAT('https://example.com/notes/', s.sectionID), 1
FROM sections s
UNION ALL
SELECT s.sectionID, 'link', CONCAT('Slides - ', s.title),
       CONCAT('https://example.com/slides/', s.sectionID), 1
FROM sections s;

-- 12. Insert Assignments (2 per course)
INSERT INTO assignments (courseID, title, description, duedate, maxgrade, created_by)
SELECT
    c.courseID,
    CONCAT('Assignment 1 - ', c.ccode),
    'First assignment for this course.',
    DATE_ADD('2025-02-15', INTERVAL MOD(c.courseID, 30) DAY),
    100.00,
    1
FROM courses c
UNION ALL
SELECT
    c.courseID,
    CONCAT('Assignment 2 - ', c.ccode),
    'Second assignment for this course.',
    DATE_ADD('2025-03-15', INTERVAL MOD(c.courseID, 30) DAY),
    100.00,
    1
FROM courses c;

-- 13. Insert Submissions with grades (set-based, no DELIMITER needed)
INSERT IGNORE INTO submissions (assignmentID, studID, grade, graded_by, graded_at)
SELECT
    1 + MOD(u.userID * 3, 400) AS assignmentID,
    u.userID AS studID,
    ROUND(50 + (RAND() * 50), 2) AS grade,
    1 AS graded_by,
    NOW() AS graded_at
FROM users u
WHERE u.role = 'student'
  AND u.userID <= 702
LIMIT 1000;
