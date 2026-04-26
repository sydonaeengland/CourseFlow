from flask import Flask, request, make_response, jsonify, send_from_directory
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt, get_jwt_identity
from flask_httpauth import HTTPBasicAuth
import mysql.connector
import bcrypt
from functools import wraps
from dotenv import load_dotenv
import os
 
app = Flask(__name__)
 
auth = HTTPBasicAuth()
load_dotenv()
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)
 
def get_db_connection():
    connection = mysql.connector.connect(
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        host=os.getenv('DB_HOST')
    )
    return connection
 
def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorated(*args, **kwargs):
            role = get_jwt()['role']
            if role not in roles:
                return jsonify({"message": "Access denied"}), 403
            return fn(*args, **kwargs)
        return decorated
    return wrapper

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')
 
# GET ALL USERS
@app.route('/users', methods=['GET'])
def get_users():
    try:
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("SELECT userID, username, email, fname, lname, role FROM users")
                rows = cursor.fetchall()
                users = [{"userID": r[0], "username": r[1], "email": r[2], "fname": r[3], "lname": r[4], "role": r[5]} for r in rows]
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
 
# REGISTER USER
@app.route('/register', methods=['POST'])
def register():
    try:
        new_user = request.get_json()
        username = new_user['username']
        password = new_user['password']
        email = new_user['email']
        fname = new_user['fname']
        lname = new_user['lname']
        role = new_user['role']
 
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    return jsonify({"message": "User already exists"}), 400
 
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute("INSERT INTO users (username, password, email, fname, lname, role) VALUES (%s, %s, %s, %s, %s, %s)",
                               (username, hashed, email, fname, lname, role))
                cnx.commit()
        return jsonify({"message": "Account created successfully"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400
 
# USER LOGIN
@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.json.get('username', None)
        password = request.json.get('password', None)
 
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("SELECT userID, username, password, fname, lname, role FROM users WHERE username = %s", (username,))
                row = cursor.fetchone()
                if row is None:
                    return make_response({'error': 'Invalid credentials'}, 401)
                userID, db_username, stored_hash, fname, lname, role = row
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                    access_token = create_access_token(identity=str(userID), additional_claims={"role": role})
                    return make_response({'success': 'Login successful', 'access_token': access_token}, 200)
                else:
                    return make_response({'error': 'Invalid credentials'}, 401)
    except Exception as e:
        return jsonify({"message": str(e)}), 400
 
# CREATE COURSE
@app.route('/courses', methods=['POST'])
@role_required('admin')
def create_course():
    try:
        new_course = request.get_json()
        ccode = new_course['ccode']
        cname = new_course['cname']
        desc = new_course['description']
        created_by = get_jwt_identity()
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("SELECT * FROM courses WHERE ccode = %s", (ccode,))
                if cursor.fetchone():
                    return jsonify({"message": "Course already exists"}), 400
                cursor.execute("INSERT INTO courses (ccode, cname, description, created_by) VALUES (%s, %s, %s, %s)",
                               (ccode, cname, desc, created_by))
                cnx.commit()
        return jsonify({"message": "Course created successfully"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400
 
# RETRIEVE ALL COURSES
@app.route('/courses', methods=['GET'])
def get_courses():
    try:
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("SELECT courseID, ccode, cname, description FROM courses")
                rows = cursor.fetchall()
                courses = [{"courseID": r[0], "ccode": r[1], "cname": r[2], "description": r[3]} for r in rows]
        return jsonify(courses), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
 
# RETRIEVE COURSES BY STUDENT
@app.route('/courses/student/<int:studID>', methods=['GET'])
def get_course_by_student(studID):
    try:
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("""
                    SELECT c.ccode, c.cname, c.description
                    FROM courses c JOIN enrollments e ON c.courseID = e.courseID
                    WHERE e.studID = %s""", (studID,))
                rows = cursor.fetchall()
                courses = [{"ccode": r[0], "cname": r[1], "description": r[2]} for r in rows]
        return jsonify(courses), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
 
# RETRIEVE COURSES BY LECTURER
@app.route('/courses/lecturer/<int:lecturerID>', methods=['GET'])
def get_course_by_lecturer(lecturerID):
    try:
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("""
                    SELECT c.ccode, c.cname, c.description, u.fname, u.lname
                    FROM courses c JOIN users u ON c.lecturerID = u.userID
                    WHERE c.lecturerID = %s""", (lecturerID,))
                rows = cursor.fetchall()
                courses = [{"ccode": r[0], "cname": r[1], "description": r[2], "fname": r[3], "lname": r[4]} for r in rows]
        return jsonify(courses), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
 
# REGISTER FOR COURSE
@app.route('/courses/<int:courseID>/enroll', methods=['POST'])
@jwt_required()
def enroll_student(courseID):
    try:
        data = request.get_json()
        studID = data ['studID']
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("INSERT INTO enrollments (courseID, studID) VALUES (%s, %s)", (courseID, studID))
                cnx.commit()
        return jsonify({"message": "Student enrolled successfully"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400
 
#ASSIGN LECTURER
@app.route('/courses/<int:courseID>/assign-lecturer', methods=['POST'])
@role_required('admin')
def assign_lecturer(courseID):
    try:
        data = request.get_json()
        lecturerID = data['lecturerID']
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("UPDATE courses SET lecturerID = %s WHERE courseID = %s", (lecturerID, courseID))
                cnx.commit()
        return jsonify ({"message": "Lecturer assigned successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
   
# RETRIEVE MEMBERS
@app.route('/courses/<int:courseID>/members', methods=['GET'])
@jwt_required()
def retrieve_members(courseID):
    try:
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("""
                    SELECT u.userID, u.username, u.fname, u.lname, u.role
                    FROM users u JOIN enrollments e ON u.userID = e.studID
                    WHERE e.courseID = %s""", (courseID,))
                rows = cursor.fetchall()
                members = [{"userID": r[0], "username": r[1], "fname": r[2], "lname": r[3], "role": r[4]} for r in rows]
        return jsonify(members), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
 
# RETRIEVE CALENDAR EVENTS
@app.route('/courses/<int:courseID>/events', methods=['GET'])
@jwt_required()
def get_events(courseID):
    try:
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("""
                    SELECT eventID, title, description, event_date, start_time, end_time
                    FROM calendar_events WHERE courseID = %s""", (courseID,))
                rows = cursor.fetchall()
                events = [{"eventID": r[0], "title": r[1], "description": r[2], "event_date": str(r[3]), "start_time": str(r[4]), "end_time": str(r[5])} for r in rows]
        return jsonify(events), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
 
# GET EVENT BY DATE
@app.route('/students/<int:studID>/events', methods=['GET'])
@jwt_required()
def get_event_by_date(studID):
    try:
        date = request.args.get('date')
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("""
                    SELECT ce.eventID, ce.title, ce.description, ce.event_date, ce.start_time, ce.end_time
                    FROM calendar_events ce
                    JOIN enrollments e ON ce.courseID = e.courseID
                    WHERE e.studID = %s AND ce.event_date = %s""", (studID, date))
                rows = cursor.fetchall()
                events = [{"eventID": r[0], "title": r[1], "description": r[2], "event_date": str(r[3]), "start_time": str(r[4]), "end_time": str(r[5])} for r in rows]
        return jsonify(events), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
 
# CREATE CALENDAR EVENTS
@app.route('/courses/<int:courseID>/events', methods=['POST'])
@role_required('lecturer', 'admin')
def create_event(courseID):
    try:
        data = request.get_json()
        title = data['title']
        description = data.get('description', '')
        event_date = data['event_date']
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        created_by = get_jwt_identity()
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO calendar_events (courseID, title, description, event_date, start_time, end_time, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)""", (courseID, title, description, event_date, start_time, end_time, created_by))
                cnx.commit()
        return jsonify({"message": "Event created successfully"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400
 
# FORUMS
@app.route('/courses/<int:courseID>/forums', methods=['GET'])
@jwt_required()
def get_forums_by_course(courseID):
    try:
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("SELECT forumID, title, created_at FROM forums WHERE courseID = %s", (courseID,))
                rows = cursor.fetchall()
                forums = [{"forumID": r[0], "title": r[1], "created_at": str(r[2])} for r in rows]
        return jsonify(forums), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
 
#CREATE FORUM
@app.route('/courses/<int:courseID>/forums', methods=['POST'])
@jwt_required()
def create_forum(courseID):
    try:
        data = request.get_json()
        title = data['title']
        created_by = get_jwt_identity()
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("INSERT INTO forums (courseID, title, created_by) VALUES (%s, %s, %s)", (courseID, title, created_by))
                cnx.commit()
        return jsonify({"message": "Forum created successfully"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400
 
# DISCUSSION THREADS
@app.route('/forums/<int:forumID>/threads', methods=['GET'])
@jwt_required()
def get_threads_by_forum(forumID):
    try:
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("SELECT threadID, title, body, created_at FROM threads WHERE forumID = %s", (forumID,))
                rows = cursor.fetchall()
                threads = [{"threadID": r[0], "title": r[1], "body": r[2], "created_at": str(r[3])} for r in rows]
        return jsonify(threads), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
   
#CREATE THREAD
@app.route('/forums/<int:forumID>/threads', methods=['POST'])
@jwt_required()
def create_thread(forumID):
    try:
        data = request.get_json()
        title = data['title']
        body = data['body']
        created_by = get_jwt_identity()
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("INSERT INTO threads (forumID, title, body, created_by) VALUES (%s, %s, %s, %s)", (forumID, title, body, created_by))
                cnx.commit()
        return jsonify({"message": "Thread created successfully"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400
 
#THREAD REPLIES
@app.route('/threads/<int:threadID>/replies', methods=['POST'])
@jwt_required()
def reply_to_thread(threadID):
    try:
        data = request.get_json()
        body = data['body']
        parentID = data.get('parentID', None)  # None if it's a top-level reply
        created_by = get_jwt_identity()
 
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO replies (threadID, parentID, body, created_by)
                    VALUES (%s, %s, %s, %s)""",
                    (threadID, parentID, body, created_by))
                cnx.commit()
        return jsonify({"message": "Reply added successfully"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400
 
# COURSE CONTENT
@app.route('/courses/<int:courseID>/content', methods=['GET'])
@jwt_required()
def get_content_by_section(courseID):
    try:
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("""
                    SELECT s.sectionID, s.title, s.position,
                           i.itemID, i.type, i.title, i.url, i.filepath
                    FROM sections s
                    LEFT JOIN items i ON s.sectionID = i.sectionID
                    WHERE s.courseID = %s
                    ORDER BY s.position, i.itemID""", (courseID,))
                rows = cursor.fetchall()
 
                sections = {}
                for r in rows:
                    sid = r[0]
                    if sid not in sections:
                        sections[sid] = {
                            "sectionID": r[0],
                            "title": r[1],
                            "position": r[2],
                            "items": []
                        }
                    if r[3]:  # only add item if it exists
                        sections[sid]["items"].append({
                            "itemID": r[3],
                            "type": r[4],
                            "title": r[5],
                            "url": r[6],
                            "filepath": r[7]
                        })
 
        return jsonify(list(sections.values())), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
 
#ADD CONTENT
@app.route('/sections/<int:sectionID>/content', methods=['POST'])
@role_required('lecturer', 'admin')
def add_content(sectionID):
    try:
        data = request.get_json()
        type = data['type']        # 'link', 'file', or 'slide'
        title = data['title']
        url = data.get('url', None)
        filepath = data.get('filepath', None)
        uploaded_by = get_jwt_identity()
 
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO items (sectionID, type, title, url, filepath, uploaded_by)
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                    (sectionID, type, title, url, filepath, uploaded_by))
                cnx.commit()
        return jsonify({"message": "Content added successfully"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400
 
# SUBMIT ASSIGNMENTS
@app.route('/courses/<int:courseID>/assignments/<int:assignmentID>/submit', methods=['POST'])
@role_required('student')
def submit_assignment(courseID, assignmentID):
    try:
        data = request.get_json()
        filepath = data.get('filepath', None)
        studID = data['studID']
 
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                # Check if student is enrolled in the course
                cursor.execute("""
                    SELECT * FROM enrollments
                    WHERE courseID = %s AND studID = %s""", (courseID, studID))
                if not cursor.fetchone():
                    return jsonify({"message": "Student is not enrolled in this course"}), 403
               
                # Check if already submitted
                cursor.execute("""
                    SELECT * FROM submissions
                    WHERE assignmentID = %s AND studID = %s""", (assignmentID, studID))
                if cursor.fetchone():
                    return jsonify({"message": "Assignment already submitted"}), 400
 
                cursor.execute("""
                    INSERT INTO submissions (assignmentID, studID, filepath)
                    VALUES (%s, %s, %s)""", (assignmentID, studID, filepath))
                cnx.commit()
        return jsonify({"message": "Assignment submitted successfully"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400
   
 
#GRADE ASSIGNMENT
@app.route('/submissions/<int:subID>/grade', methods=['POST'])
@role_required('lecturer', 'admin')
def grade_assignment(subID):
    try:
        data = request.get_json()
        grade = data['grade']
        graded_by = get_jwt_identity()
 
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                # Check if submission exists
                cursor.execute("""
                    SELECT * FROM submissions
                    WHERE subID = %s""", (subID,))
                if not cursor.fetchone():
                    return jsonify({"message": "Submission not found"}), 404
 
                cursor.execute("""
                    UPDATE submissions
                    SET grade = %s, graded_by = %s, graded_at = NOW()
                    WHERE subID = %s""", (grade, graded_by, subID))
                cnx.commit()
        return jsonify({"message": "Submission graded successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
 
# REPORTS
@app.route('/reports/courses', methods=['GET'])
@role_required('admin')
def get_courses_report():
    try:
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("SELECT * FROM vw_courses_50_plus")
                rows = cursor.fetchall()
                courses = [{"courseID": r[0], "ccode": r[1], "cname": r[2], "student_count": r[3]} for r in rows]
        return jsonify(courses), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
 
#GET STUDENTS REPORTS
@app.route('/reports/students', methods=['GET'])
@role_required('admin')
def get_students_report():
    try:
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("SELECT * FROM vw_students_5_plus_courses")
                rows = cursor.fetchall()
                students = [{"userID": r[0], "username": r[1], "fname": r[2], "lname": r[3], "course_count": r[4]} for r in rows]
        return jsonify(students), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
   
#GET LECTURERS REPORTS
@app.route('/reports/lecturers', methods=['GET'])
@role_required('admin')
def get_lecturers_report():
    try:
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("SELECT * FROM vw_lecturers_3_plus_courses")
                rows = cursor.fetchall()
                lecturers = [{"userID": r[0], "username": r[1], "fname": r[2], "lname": r[3], "course_count": r[4]} for r in rows]
        return jsonify(lecturers), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
   
 
#GET TOP ENROLLED
@app.route('/reports/top-10-enrolled', methods=['GET'])
def get_top_enrolled():
    try:
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("SELECT * FROM vw_top_10_enrolled_courses")
                rows = cursor.fetchall()
                courses = [{"courseID": r[0], "ccode": r[1], "cname": r[2], "student_count": r[3]} for r in rows]
        return jsonify(courses), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

#GET TOP STUDENTS
@app.route('/reports/top-10-students', methods=['GET'])
@role_required('lecturer', 'admin')
def get_top_students():
    try:
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("SELECT * FROM vw_top_10_students_avg")
                rows = cursor.fetchall()
                students = [{"userID": r[0], "username": r[1], "fname": r[2], "lname": r[3], "overall_average": r[4]} for r in rows]
        return jsonify(students), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
 
if __name__ == '__main__':
    app.run(debug=True)