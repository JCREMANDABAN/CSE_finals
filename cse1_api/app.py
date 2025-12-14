from flask import Flask, jsonify, request, Response
from dicttoxml import dicttoxml
import jwt, datetime
from functools import wraps
import db

app = Flask(__name__)

# Replace with environment variable in production
SECRET = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"

def format_response(data, fmt="json"):
    fmt = (fmt or "json").lower()
    if fmt == "xml":
        root = 'student' if isinstance(data, dict) else 'students'
        xml_bytes = dicttoxml(data, custom_root=root, attr_type=False)
        return Response(xml_bytes, mimetype="application/xml")
    elif fmt == "json":
        return jsonify(data)
    return jsonify({"error": "Unsupported format"}), 406

def validate_student_payload(data):
    errors = []
    if not isinstance(data.get('name'), str) or not data['name'].strip():
        errors.append("name is required and must be a non-empty string")
    if not isinstance(data.get('course'), str) or not data['course'].strip():
        errors.append("course is required and must be a non-empty string")
    yl = data.get('year_level')
    if not isinstance(yl, int) or not (1 <= yl <= 5):
        errors.append("year_level must be an integer between 1 and 5")
    return errors

def require_jwt(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error":"Missing Bearer token"}), 401
        token = auth.split(" ",1)[1]
        try:
            jwt.decode(token, SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error":"Token expired"}), 401
        except Exception:
            return jsonify({"error":"Invalid token"}), 401
        return f(*args, **kwargs)
    return wrapper

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK"}), 200

@app.route('/auth/login', methods=['POST'])
def login():
    creds = request.get_json() or {}
    # Demo credentials only
    if creds.get('username') != 'admin' or creds.get('password') != 'admin123':
        return jsonify({"error":"Invalid credentials"}), 401
    payload = {"sub":"admin","exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)}
    token = jwt.encode(payload, SECRET, algorithm="HS256")
    return jsonify({"token": token})

# GET all students
@app.route('/students', methods=['GET'])
def get_students():
    fmt = request.args.get('format', 'json')
    conn = db.get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students;")
        rows = cursor.fetchall()
        return format_response(rows, fmt), 200
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        conn.close()

# GET single student by ID
@app.route('/students/<int:sid>', methods=['GET'])
def get_student(sid):
    fmt = request.args.get('format', 'json')
    conn = db.get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students WHERE id = %s;", (sid,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "Student not found"}), 404
        return format_response(row, fmt), 200
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        conn.close()

# Search students
@app.route('/students/search', methods=['GET'])
def search_students():
    fmt = request.args.get('format', 'json')
    name = request.args.get('name')
    course = request.args.get('course')
    year_level = request.args.get('year_level', type=int)

    clauses, params = [], []
    if name:
        clauses.append("name LIKE %s")
        params.append(f"%{name}%")
    if course:
        clauses.append("course = %s")
        params.append(course)
    if year_level is not None:
        clauses.append("year_level = %s")
        params.append(year_level)

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    conn = db.get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM students {where};", tuple(params))
        rows = cursor.fetchall()
        return format_response(rows, fmt), 200
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        conn.close()

# POST add student
@app.route('/students', methods=['POST'])
@require_jwt
def add_student():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415
    data = request.get_json(silent=True) or {}
    errors = validate_student_payload(data)
    if errors:
        return jsonify({"errors": errors}), 400

    conn = db.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students (name, course, year_level) VALUES (%s, %s, %s);",
            (data['name'], data['course'], data['year_level'])
        )
        conn.commit()
        new_id = cursor.lastrowid
        return jsonify({"message": "Student added", "id": new_id}), 201
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        conn.close()

# PUT update student
@app.route('/students/<int:sid>', methods=['PUT'])
@require_jwt
def update_student(sid):
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415
    data = request.get_json(silent=True) or {}
    errors = validate_student_payload(data)
    if errors:
        return jsonify({"errors": errors}), 400

    conn = db.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE students SET name=%s, course=%s, year_level=%s WHERE id=%s;",
            (data['name'], data['course'], data['year_level'], sid)
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Student not found"}), 404
        return jsonify({"message": "Student updated"}), 200
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        conn.close()

# DELETE student
@app.route('/students/<int:sid>', methods=['DELETE'])
@require_jwt
def delete_student(sid):
    conn = db.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id=%s;", (sid,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Student not found"}), 404
        return jsonify({"message": "Student deleted"}), 200
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
