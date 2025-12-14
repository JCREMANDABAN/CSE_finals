from flask import Flask, request, jsonify, Response
import db
from dicttoxml import dicttoxml

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "API is running",
        "endpoints": ["/health", "/students", "/students/<id>"]
    })


def format_response(data, fmt="json"):
    if fmt == "xml":
        xml_bytes = dicttoxml(data, custom_root='students', attr_type=False)
        return Response(xml_bytes, mimetype="application/xml")
    return jsonify(data)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK"}), 200

# GET all students
@app.route('/students', methods=['GET'])
def get_students():
    fmt = request.args.get('format', 'json')
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students;")
    rows = cursor.fetchall()
    conn.close()
    return format_response(rows, fmt)

# GET single student by ID
@app.route('/students/<int:sid>', methods=['GET'])
def get_student(sid):
    fmt = request.args.get('format', 'json')
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE id = %s;", (sid,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Student not found"}), 404
    return format_response(row, fmt)

# POST add student
@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()
    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO students (name, course, year_level) VALUES (%s, %s, %s);",
        (data['name'], data['course'], data['year_level'])
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"message": "Student added", "id": new_id}), 201

# PUT update student
@app.route('/students/<int:sid>', methods=['PUT'])
def update_student(sid):
    data = request.get_json()
    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE students SET name=%s, course=%s, year_level=%s WHERE id=%s;",
        (data['name'], data['course'], data['year_level'], sid)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Student updated"}), 200

# DELETE student
@app.route('/students/<int:sid>', methods=['DELETE'])
def delete_student(sid):
    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id=%s;", (sid,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Student deleted"}), 200

if __name__ == '__main__':
    app.run(debug=True)
