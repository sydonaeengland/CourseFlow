from flask import Flask, request, make_response, jsonify, send_from_directory
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt, get_jwt_identity
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS
import mysql.connector
from mysql.connector import pooling
import bcrypt
from functools import wraps
from dotenv import load_dotenv
from datetime import timedelta
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

auth = HTTPBasicAuth()
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
jwt = JWTManager(app)

_pool = None

def get_db_connection():
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name='cf_pool',
            pool_size=10,
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 3306))
        )
    return _pool.get_connection()
 
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
    return send_from_directory('.', 'auth.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)
 
# GET ALL USERS
@app.route('/users', methods=['GET'])
def get_users():
    try:
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                role = request.args.get('role')
                if role:
                    cursor.execute("SELECT userID, username, email, fname, lname, role FROM users WHERE role = %s LIMIT 500", (role,))
                else:
                    cursor.execute("SELECT userID, username, email, fname, lname, role FROM users LIMIT 500")
                rows = cursor.fetchall()
                users = [{"userID": r[0], "username": r[1], "email": r[2], "fname": r[3], "lname": r[4], "role": r[5]} for r in rows]
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

# GET SINGLE USER
@app.route('/users/<int:userID>', methods=['GET'])
@jwt_required()
def get_user(userID):
    try:
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("SELECT userID, username, email, fname, lname, role FROM users WHERE userID = %s", (userID,))
                r = cursor.fetchone()
                if not r:
                    return jsonify({"message": "User not found"}), 404
                user = {"userID": r[0], "username": r[1], "email": r[2], "fname": r[3], "lname": r[4], "role": r[5]}
        return jsonify(user), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

# CHANGE PASSWORD
@app.route('/users/<int:userID>/password', methods=['PUT'])
@jwt_required()
def change_password(userID):
    try:
        data = request.get_json()
        current_password = data['current_password']
        new_password = data['new_password']
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("SELECT password FROM users WHERE userID = %s", (userID,))
                row = cursor.fetchone()
                if not row:
                    return jsonify({"message": "User not found"}), 404
                if not bcrypt.checkpw(current_password.encode('utf-8'), row[0].encode('utf-8')):
                    return jsonify({"message": "Current password is incorrect"}), 401
                hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute("UPDATE users SET password = %s WHERE userID = %s", (hashed, userID))
                cnx.commit()
        return jsonify({"message": "Password updated successfully"}), 200
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
        ccode      = new_course['ccode']
        cname      = new_course['cname']
        desc       = new_course.get('description', '')
        lecturerID = new_course.get('lecturerID')
        created_by = get_jwt_identity()
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("SELECT * FROM courses WHERE ccode = %s", (ccode,))
                if cursor.fetchone():
                    return jsonify({"message": "Course already exists"}), 400
                cursor.execute("""
                    INSERT INTO courses (ccode, cname, description, created_by, lecturerID)
                    VALUES (%s, %s, %s, %s, %s)""",
                    (ccode, cname, desc, created_by, lecturerID))
                cnx.commit()
        return jsonify({"message": "Course created successfully"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400
 
# RETRIEVE SINGLE COURSE
@app.route('/courses/<int:courseID>', methods=['GET'])
@jwt_required()
def get_course(courseID):
    try:
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("""
                    SELECT c.courseID, c.ccode, c.cname, c.description,
                           u.fname, u.lname, u.userID as lecturerID, u.email
                    FROM courses c
                    LEFT JOIN users u ON c.lecturerID = u.userID
                    WHERE c.courseID = %s""", (courseID,))
                r = cursor.fetchone()
                if not r:
                    return jsonify({"message": "Course not found"}), 404
                course = {"courseID": r[0], "ccode": r[1], "cname": r[2], "description": r[3],
                          "fname": r[4], "lname": r[5], "lecturerID": r[6], "email": r[7]}
        return jsonify(course), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

# RETRIEVE ALL COURSES
@app.route('/courses', methods=['GET'])
def get_courses():
    try:
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("""
                    SELECT c.courseID, c.ccode, c.cname, c.description,
                           u.fname, u.lname, u.userID as lecturerID
                    FROM courses c
                    LEFT JOIN users u ON c.lecturerID = u.userID
                    ORDER BY c.ccode""")
                rows = cursor.fetchall()
                courses = [{"courseID": r[0], "ccode": r[1], "cname": r[2], "description": r[3],
                            "fname": r[4], "lname": r[5], "lecturerID": r[6]} for r in rows]
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
                    SELECT c.courseID, c.ccode, c.cname, c.description
                    FROM courses c JOIN enrollments e ON c.courseID = e.courseID
                    WHERE e.studID = %s""", (studID,))
                rows = cursor.fetchall()
                courses = [{"courseID": r[0], "ccode": r[1], "cname": r[2], "description": r[3]} for r in rows]
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
                    SELECT c.courseID, c.ccode, c.cname, c.description, u.fname, u.lname,
                           COUNT(e.studID) AS student_count
                    FROM courses c
                    JOIN users u ON c.lecturerID = u.userID
                    LEFT JOIN enrollments e ON c.courseID = e.courseID
                    WHERE c.lecturerID = %s
                    GROUP BY c.courseID, c.ccode, c.cname, c.description, u.fname, u.lname""", (lecturerID,))
                rows = cursor.fetchall()
                courses = [{"courseID": r[0], "ccode": r[1], "cname": r[2], "description": r[3],
                            "fname": r[4], "lname": r[5], "student_count": r[6]} for r in rows]
        return jsonify(courses), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

# UPDATE COURSE DESCRIPTION (lecturer of that course or admin)
@app.route('/courses/<int:courseID>', methods=['PATCH'])
@jwt_required()
def update_course(courseID):
    try:
        userID = int(get_jwt_identity())
        data = request.get_json()
        description = data.get('description', '').strip()
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("SELECT lecturerID FROM courses WHERE courseID=%s", (courseID,))
                row = cursor.fetchone()
                if not row:
                    return jsonify({"message": "Course not found"}), 404
                cursor.execute("SELECT role FROM users WHERE userID=%s", (userID,))
                user = cursor.fetchone()
                if user[0] != 'admin' and row[0] != userID:
                    return jsonify({"message": "Not authorized"}), 403
                cursor.execute("UPDATE courses SET description=%s WHERE courseID=%s", (description, courseID))
                cnx.commit()
        return jsonify({"message": "Course updated"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

# REGISTER FOR COURSE
@app.route('/courses/<int:courseID>/enroll', methods=['POST'])
@jwt_required()
def enroll_student(courseID):
    try:
        data = request.get_json()
        studID = data['studID']
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("INSERT INTO enrollments (courseID, studID) VALUES (%s, %s)", (courseID, studID))
                cnx.commit()
        return jsonify({"message": "Student enrolled successfully"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400

# DROP COURSE
@app.route('/courses/<int:courseID>/enroll', methods=['DELETE'])
@jwt_required()
def drop_course(courseID):
    try:
        data = request.get_json()
        studID = data['studID']
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("DELETE FROM enrollments WHERE courseID = %s AND studID = %s", (courseID, studID))
                cnx.commit()
        return jsonify({"message": "Course dropped successfully"}), 200
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
                    FROM calendar_events WHERE courseID = %s
                    ORDER BY event_date ASC, start_time ASC""", (courseID,))
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
 
# GET SINGLE FORUM
@app.route('/forums/<int:forumID>', methods=['GET'])
@jwt_required()
def get_forum(forumID):
    try:
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("""
                    SELECT f.forumID, f.title, f.courseID, f.created_at,
                           c.ccode, c.cname
                    FROM forums f JOIN courses c ON f.courseID = c.courseID
                    WHERE f.forumID = %s""", (forumID,))
                r = cursor.fetchone()
                if not r:
                    return jsonify({"message": "Forum not found"}), 404
                forum = {"forumID": r[0], "title": r[1], "courseID": r[2],
                         "created_at": str(r[3]), "ccode": r[4], "cname": r[5]}
        return jsonify(forum), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

# DISCUSSION THREADS
@app.route('/forums/<int:forumID>/threads', methods=['GET'])
@jwt_required()
def get_threads_by_forum(forumID):
    try:
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("""
                    SELECT t.threadID, t.title, t.body, t.created_at,
                           u.userID, u.username, u.fname, u.lname
                    FROM threads t
                    JOIN users u ON t.created_by = u.userID
                    WHERE t.forumID = %s
                    ORDER BY t.created_at DESC""", (forumID,))
                rows = cursor.fetchall()
                threads = [{"threadID": r[0], "title": r[1], "body": r[2], "created_at": str(r[3]),
                            "userID": r[4], "username": r[5], "fname": r[6], "lname": r[7]} for r in rows]
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
 
# DELETE THREAD (owner or admin only)
@app.route('/threads/<int:threadID>', methods=['DELETE'])
@jwt_required()
def delete_thread(threadID):
    try:
        user_id = int(get_jwt_identity())
        role = get_jwt()['role']
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("SELECT created_by FROM threads WHERE threadID = %s", (threadID,))
                row = cursor.fetchone()
                if not row:
                    return jsonify({"message": "Thread not found"}), 404
                if role != 'admin' and row[0] != user_id:
                    return jsonify({"message": "Not authorised"}), 403
                cursor.execute("DELETE FROM replies WHERE threadID = %s", (threadID,))
                cursor.execute("DELETE FROM threads WHERE threadID = %s", (threadID,))
                cnx.commit()
        return jsonify({"message": "Thread deleted"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

# DELETE REPLY (owner or admin only)
@app.route('/replies/<int:replyID>', methods=['DELETE'])
@jwt_required()
def delete_reply(replyID):
    try:
        user_id = int(get_jwt_identity())
        role = get_jwt()['role']
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("SELECT created_by FROM replies WHERE replyID = %s", (replyID,))
                row = cursor.fetchone()
                if not row:
                    return jsonify({"message": "Reply not found"}), 404
                if role != 'admin' and row[0] != user_id:
                    return jsonify({"message": "Not authorised"}), 403
                cursor.execute("DELETE FROM replies WHERE replyID = %s OR parentID = %s", (replyID, replyID))
                cnx.commit()
        return jsonify({"message": "Reply deleted"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

#GET THREAD REPLIES
@app.route('/threads/<int:threadID>/replies', methods=['GET'])
@jwt_required()
def get_replies(threadID):
    try:
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("""
                    SELECT r.replyID, r.parentID, r.body, r.created_at,
                           u.userID, u.username, u.fname, u.lname
                    FROM replies r
                    JOIN users u ON r.created_by = u.userID
                    WHERE r.threadID = %s
                    ORDER BY r.created_at ASC""", (threadID,))
                rows = cursor.fetchall()
                replies = [{"replyID": r[0], "parentID": r[1], "body": r[2],
                            "created_at": str(r[3]), "userID": r[4],
                            "username": r[5], "fname": r[6], "lname": r[7]} for r in rows]
        return jsonify(replies), 200
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
                        sections[sid] = {"sectionID": sid, "title": r[1], "position": r[2], "items": []}
                    if r[3]:
                        sections[sid]["items"].append({
                            "itemID": r[3], "type": r[4], "title": r[5], "url": r[6], "filepath": r[7]
                        })

        result = sorted(sections.values(), key=lambda s: s['position'])
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
 
# CREATE SECTION
@app.route('/courses/<int:courseID>/sections', methods=['POST'])
@role_required('lecturer', 'admin')
def create_section(courseID):
    try:
        data = request.get_json()
        title = data['title']
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("SELECT COALESCE(MAX(position),0)+1 FROM sections WHERE courseID=%s", (courseID,))
                position = cursor.fetchone()[0]
                cursor.execute("INSERT INTO sections (courseID, title, position) VALUES (%s,%s,%s)",
                               (courseID, title, position))
                cnx.commit()
                sectionID = cursor.lastrowid
        return jsonify({"message": "Section created", "sectionID": sectionID}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400

# RENAME SECTION
@app.route('/sections/<int:sectionID>', methods=['PATCH'])
@role_required('lecturer', 'admin')
def update_section(sectionID):
    try:
        data = request.get_json()
        title = data['title'].strip()
        if not title:
            return jsonify({"message": "Title required"}), 400
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("UPDATE sections SET title=%s WHERE sectionID=%s", (title, sectionID))
                cnx.commit()
        return jsonify({"message": "Section updated"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

# DELETE SECTION
@app.route('/sections/<int:sectionID>', methods=['DELETE'])
@role_required('lecturer', 'admin')
def delete_section(sectionID):
    try:
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("DELETE FROM items WHERE sectionID=%s", (sectionID,))
                cursor.execute("DELETE FROM sections WHERE sectionID=%s", (sectionID,))
                cnx.commit()
        return jsonify({"message": "Section deleted"}), 200
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
 
# GET ASSIGNMENTS FOR COURSE
@app.route('/courses/<int:courseID>/assignments', methods=['GET'])
@jwt_required()
def get_assignments(courseID):
    try:
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("""
                    SELECT assignmentID, title, description, duedate, maxgrade, created_at
                    FROM assignments WHERE courseID = %s
                    ORDER BY duedate ASC""", (courseID,))
                rows = cursor.fetchall()
                assignments = [{"assignmentID": r[0], "title": r[1], "description": r[2],
                                "duedate": str(r[3]) if r[3] else None,
                                "maxgrade": float(r[4]), "created_at": str(r[5])} for r in rows]
        return jsonify(assignments), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

# CREATE ASSIGNMENT
@app.route('/courses/<int:courseID>/assignments', methods=['POST'])
@role_required('lecturer', 'admin')
def create_assignment(courseID):
    try:
        data = request.get_json()
        title       = data['title']
        description = data.get('description', '')
        duedate     = data.get('duedate')
        maxgrade    = data.get('maxgrade', 100.00)
        created_by  = get_jwt_identity()
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO assignments (courseID, title, description, duedate, maxgrade, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                    (courseID, title, description, duedate, maxgrade, created_by))
                cnx.commit()
        return jsonify({"message": "Assignment created successfully"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400

# EDIT ASSIGNMENT
@app.route('/assignments/<int:assignmentID>', methods=['PATCH'])
@role_required('lecturer', 'admin')
def update_assignment(assignmentID):
    try:
        data = request.get_json()
        fields, values = [], []
        for key in ('title', 'description', 'duedate', 'maxgrade'):
            if key in data:
                fields.append(f"{key}=%s")
                values.append(data[key])
        if not fields:
            return jsonify({"message": "Nothing to update"}), 400
        values.append(assignmentID)
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute(f"UPDATE assignments SET {', '.join(fields)} WHERE assignmentID=%s", values)
                cnx.commit()
        return jsonify({"message": "Assignment updated"}), 200
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

# GET SUBMISSIONS FOR AN ASSIGNMENT (lecturer/admin)
@app.route('/assignments/<int:assignmentID>/submissions', methods=['GET'])
@role_required('lecturer', 'admin')
def get_submissions(assignmentID):
    try:
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("""
                    SELECT s.subID, s.studID, u.fname, u.lname, u.username,
                           s.filepath, s.submitted_at, s.grade, s.graded_at
                    FROM submissions s
                    JOIN users u ON s.studID = u.userID
                    WHERE s.assignmentID = %s
                    ORDER BY s.submitted_at ASC""", (assignmentID,))
                rows = cursor.fetchall()
                submissions = [{"subID": r[0], "studID": r[1], "fname": r[2], "lname": r[3],
                                "username": r[4], "filepath": r[5],
                                "submitted_at": str(r[6]) if r[6] else None,
                                "grade": float(r[7]) if r[7] is not None else None,
                                "graded_at": str(r[8]) if r[8] else None} for r in rows]
        return jsonify(submissions), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

# GET MY SUBMISSION FOR AN ASSIGNMENT (student)
@app.route('/assignments/<int:assignmentID>/my-submission', methods=['GET'])
@jwt_required()
def get_my_submission(assignmentID):
    try:
        studID = get_jwt_identity()
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("""
                    SELECT subID, filepath, submitted_at, grade, graded_at
                    FROM submissions WHERE assignmentID = %s AND studID = %s""",
                    (assignmentID, studID))
                row = cursor.fetchone()
        if row:
            return jsonify({"subID": row[0], "filepath": row[1],
                            "submitted_at": str(row[2]) if row[2] else None,
                            "grade": float(row[3]) if row[3] is not None else None,
                            "graded_at": str(row[4]) if row[4] else None}), 200
        return jsonify(None), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

# REPORTS
@app.route('/reports/courses', methods=['GET'])
@app.route('/reports/courses-50-plus', methods=['GET'])
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
@app.route('/reports/students-5-plus-courses', methods=['GET'])
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
@app.route('/reports/lecturers-3-plus-courses', methods=['GET'])
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
 
# GET STUDENT GRADES — all graded submissions grouped by course
@app.route('/students/<int:studID>/grades', methods=['GET'])
@jwt_required()
def get_student_grades(studID):
    try:
        caller_id = int(get_jwt_identity())
        caller_role = get_jwt()['role']
        if caller_role == 'student' and caller_id != studID:
            return jsonify({"message": "Not authorised"}), 403
        with get_db_connection() as cnx:
            with cnx.cursor() as cursor:
                cursor.execute("""
                    SELECT c.courseID, c.ccode, c.cname,
                           a.assignmentID, a.title, a.maxgrade,
                           s.grade, s.submitted_at, s.graded_at,
                           ROUND(AVG(s.grade / a.maxgrade * 100) OVER (PARTITION BY c.courseID), 2) AS course_avg,
                           ROUND(AVG(s.grade / a.maxgrade * 100) OVER (), 2) AS overall_avg
                    FROM submissions s
                    JOIN assignments a ON s.assignmentID = a.assignmentID
                    JOIN courses c ON a.courseID = c.courseID
                    WHERE s.studID = %s AND s.grade IS NOT NULL
                    ORDER BY c.ccode, a.title""", (studID,))
                rows = cursor.fetchall()

        courses = {}
        overall_average = None
        for r in rows:
            cid = r[0]
            overall_average = float(r[10]) if r[10] is not None else None
            if cid not in courses:
                courses[cid] = {"courseID": cid, "ccode": r[1], "cname": r[2],
                                "course_average": float(r[9]) if r[9] is not None else None,
                                "grades": []}
            courses[cid]["grades"].append({
                "assignmentID": r[3], "title": r[4], "maxgrade": float(r[5]),
                "grade": float(r[6]), "submitted_at": str(r[7]) if r[7] else None,
                "graded_at": str(r[8]) if r[8] else None
            })
        return jsonify({"courses": list(courses.values()), "overall_average": overall_average}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)