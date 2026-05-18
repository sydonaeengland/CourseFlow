CREATE TABLE IF NOT EXISTS users (
    userID     INT AUTO_INCREMENT PRIMARY KEY,
    username   VARCHAR(50)  NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    email      VARCHAR(100) NOT NULL UNIQUE,
    fname      VARCHAR(50)  NOT NULL,
    lname      VARCHAR(50)  NOT NULL,
    role       ENUM('admin','lecturer','student') NOT NULL DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS courses (
    courseID    INT AUTO_INCREMENT PRIMARY KEY,
    ccode       VARCHAR(20)  NOT NULL UNIQUE,
    cname       VARCHAR(100) NOT NULL,
    description TEXT,
    created_by  INT NOT NULL,
    lecturerID  INT DEFAULT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(userID),
    FOREIGN KEY (lecturerID) REFERENCES users(userID)
);

CREATE TABLE IF NOT EXISTS enrollments (
    enrollmentID INT AUTO_INCREMENT PRIMARY KEY,
    courseID     INT NOT NULL,
    studID       INT NOT NULL,
    enrolled_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_enrollment (courseID, studID),
    FOREIGN KEY (courseID) REFERENCES courses(courseID),
    FOREIGN KEY (studID)   REFERENCES users(userID)
);

CREATE TABLE IF NOT EXISTS calendar_events (
    eventID     INT AUTO_INCREMENT PRIMARY KEY,
    courseID    INT NOT NULL,
    title       VARCHAR(150) NOT NULL,
    description TEXT,
    event_date  DATE NOT NULL,
    start_time  TIME,
    end_time    TIME,
    created_by  INT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (courseID)   REFERENCES courses(courseID),
    FOREIGN KEY (created_by) REFERENCES users(userID)
);

CREATE TABLE IF NOT EXISTS forums (
    forumID    INT AUTO_INCREMENT PRIMARY KEY,
    courseID   INT NOT NULL,
    title      VARCHAR(150) NOT NULL,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (courseID)   REFERENCES courses(courseID),
    FOREIGN KEY (created_by) REFERENCES users(userID)
);

CREATE TABLE IF NOT EXISTS threads (
    threadID   INT AUTO_INCREMENT PRIMARY KEY,
    forumID    INT NOT NULL,
    title      VARCHAR(200) NOT NULL,
    body       TEXT NOT NULL,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (forumID)    REFERENCES forums(forumID),
    FOREIGN KEY (created_by) REFERENCES users(userID)
);

CREATE TABLE IF NOT EXISTS replies (
    replyID    INT AUTO_INCREMENT PRIMARY KEY,
    threadID   INT NOT NULL,
    parentID   INT DEFAULT NULL,
    body       TEXT NOT NULL,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (threadID)   REFERENCES threads(threadID),
    FOREIGN KEY (parentID)   REFERENCES replies(replyID),
    FOREIGN KEY (created_by) REFERENCES users(userID)
);

CREATE TABLE IF NOT EXISTS sections (
    sectionID INT AUTO_INCREMENT PRIMARY KEY,
    courseID  INT NOT NULL,
    title     VARCHAR(150) NOT NULL,
    position  INT NOT NULL DEFAULT 0,
    FOREIGN KEY (courseID) REFERENCES courses(courseID)
);

CREATE TABLE IF NOT EXISTS items (
    itemID      INT AUTO_INCREMENT PRIMARY KEY,
    sectionID   INT NOT NULL,
    type        ENUM('link','file','slide') NOT NULL,
    title       VARCHAR(150) NOT NULL,
    url         VARCHAR(500),
    filepath    VARCHAR(500),
    uploaded_by INT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sectionID)   REFERENCES sections(sectionID),
    FOREIGN KEY (uploaded_by) REFERENCES users(userID)
);

CREATE TABLE IF NOT EXISTS assignments (
    assignmentID INT AUTO_INCREMENT PRIMARY KEY,
    courseID     INT NOT NULL,
    title        VARCHAR(150) NOT NULL,
    description  TEXT,
    duedate      DATETIME,
    maxgrade     DECIMAL(5,2) NOT NULL DEFAULT 100.00,
    created_by   INT NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (courseID)   REFERENCES courses(courseID),
    FOREIGN KEY (created_by) REFERENCES users(userID)
);

CREATE TABLE IF NOT EXISTS submissions (
    subID        INT AUTO_INCREMENT PRIMARY KEY,
    assignmentID INT NOT NULL,
    studID       INT NOT NULL,
    filepath     VARCHAR(500),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    grade        DECIMAL(5,2) DEFAULT NULL,
    graded_by    INT DEFAULT NULL,
    graded_at    TIMESTAMP DEFAULT NULL,
    UNIQUE KEY uq_submission (assignmentID, studID),
    FOREIGN KEY (assignmentID) REFERENCES assignments(assignmentID),
    FOREIGN KEY (studID)       REFERENCES users(userID),
    FOREIGN KEY (graded_by)    REFERENCES users(userID)
);

CREATE OR REPLACE VIEW vw_courses_50_plus AS
SELECT c.courseID, c.ccode, c.cname, COUNT(e.studID) AS student_count
FROM courses c JOIN enrollments e ON c.courseID = e.courseID
GROUP BY c.courseID, c.ccode, c.cname HAVING COUNT(e.studID) >= 50;

CREATE OR REPLACE VIEW vw_students_5_plus_courses AS
SELECT u.userID, u.username, u.fname, u.lname, COUNT(e.courseID) AS course_count
FROM users u JOIN enrollments e ON u.userID = e.studID
WHERE u.role = 'student'
GROUP BY u.userID, u.username, u.fname, u.lname HAVING COUNT(e.courseID) >= 5;

CREATE OR REPLACE VIEW vw_lecturers_3_plus_courses AS
SELECT u.userID, u.username, u.fname, u.lname, COUNT(c.courseID) AS course_count
FROM users u JOIN courses c ON u.userID = c.lecturerID
WHERE u.role = 'lecturer'
GROUP BY u.userID, u.username, u.fname, u.lname HAVING COUNT(c.courseID) >= 3;

CREATE OR REPLACE VIEW vw_top_10_enrolled_courses AS
SELECT c.courseID, c.ccode, c.cname, COUNT(e.studID) AS student_count
FROM courses c JOIN enrollments e ON c.courseID = e.courseID
GROUP BY c.courseID, c.ccode, c.cname ORDER BY student_count DESC LIMIT 10;

CREATE OR REPLACE VIEW vw_top_10_students_avg AS
SELECT u.userID, u.username, u.fname, u.lname, ROUND(AVG(s.grade), 2) AS overall_average
FROM users u JOIN submissions s ON u.userID = s.studID
WHERE s.grade IS NOT NULL AND u.role = 'student'
GROUP BY u.userID, u.username, u.fname, u.lname ORDER BY overall_average DESC LIMIT 10;

CREATE INDEX idx_enrollments_student ON enrollments(studID);
CREATE INDEX idx_enrollments_course  ON enrollments(courseID);
CREATE INDEX idx_submissions_student ON submissions(studID);
CREATE INDEX idx_calendar_date       ON calendar_events(event_date);
CREATE INDEX idx_threads_forum       ON threads(forumID);
CREATE INDEX idx_replies_thread      ON replies(threadID);
CREATE INDEX idx_replies_parent      ON replies(parentID);
CREATE INDEX idx_content_section     ON items(sectionID);
CREATE INDEX idx_courses_lecturer    ON courses(lecturerID);
