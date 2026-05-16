# CourseFlow

A course management system REST API built with Flask and MySQL, with a frontend web application. Built for COMP3161.

## Features

- User registration and login with JWT authentication
- Role-based access control (admin, lecturer, student)
- Course creation and enrollment
- Forums and discussion threads
- Calendar events
- Course content (sections and items)
- Assignments and grading
- Admin reports and views

## Tech Stack

- **Backend:** Python, Flask
- **Database:** MySQL 8
- **Auth:** JWT (Flask-JWT-Extended)
- **Frontend:** HTML, CSS, JavaScript
- **Containerization:** Docker, Docker Compose

## Running with Docker (Recommended)

1. Clone the repo
2. Create a `.env` file in the root folder:

```
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=course_management
DB_HOST=localhost
JWT_SECRET_KEY=anyrandomstring
```

3. Start the containers:

```bash
docker compose up --build
```

The API will be available at `http://localhost:5000`.

The database is seeded automatically on first run with:
- 1 admin account
- 200 lecturers
- 100,000 students
- 200 courses
- Forums, events, assignments, and course content

**Default password for all seeded accounts:** `password123`

## Running Locally (Without Docker)

1. Clone the repo
2. Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file as shown above
5. Run the database scripts against your local MySQL instance:

```bash
mysql -u root -p < create_db.sql
mysql -u root -p < populate_db.sql
```

6. Start the server:

```bash
python app.py
```

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/register` | Register a new user | None |
| POST | `/login` | Login and get JWT token | None |
| GET | `/courses` | Get all courses | JWT |
| POST | `/courses` | Create a course | Admin |
| GET | `/courses/<id>` | Get a single course | JWT |
| GET | `/courses/<id>/members` | Get course members | JWT |
| POST | `/courses/<id>/enroll` | Enroll in a course | JWT |
| GET | `/courses/<id>/forums` | Get course forums | JWT |
| POST | `/courses/<id>/forums` | Create a forum | JWT |
| GET | `/forums/<id>/threads` | Get threads in a forum | JWT |
| POST | `/forums/<id>/threads` | Create a thread | JWT |
| GET | `/courses/<id>/events` | Get calendar events | JWT |
| POST | `/courses/<id>/events` | Create a calendar event | JWT |
| GET | `/courses/<id>/content` | Get course content | JWT |
| POST | `/courses/<id>/sections` | Add a section | Lecturer |
| GET | `/courses/<id>/assignments` | Get assignments | JWT |
| POST | `/courses/<id>/assignments` | Create an assignment | Lecturer |
| POST | `/assignments/<id>/submit` | Submit an assignment | Student |
| PUT | `/assignments/<id>/grade/<studID>` | Grade a submission | Lecturer |
