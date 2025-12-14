from flask import Flask, request, jsonify, Response
import db
from dicttoxml import dicttoxml

app = Flask(__name__)

def format_response(data, fmt="json"):
    if fmt == "xml":
        xml_bytes = dicttoxml(data, custom_root='student', attr_type=False)
        return Response(xml_bytes, mimetype="application/xml")
    else:
        return jsonify(data)
    
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK"}), 200

@app.route('/student', methods=['GET'])
def get_student():
    fmt = request.args.get('format', 'json')
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students LIMIT 1;")
    rows = cursor.fetchall()
    conn.close()
    return format_response(rows, fmt)

@app.route('/students', methods=['GET'])
def get_students(sid):
    fmt = request.args.get('format', 'json')
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE sid = %s;", (sid,))
    rows = cursor.fetchone()
    conn.close()
    if not rows:
        return jsonify({"error": "Student not found"}), 404
    return format_response(rows, fmt)

@app.route('/students', methods=['POST'])
def add_student():
    data = request.json()
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO students (fullname, course, year_level) VALUES (%s, %s, %s);",
        (data['fullname'], data['course'], data['year_level'])
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"message": "Student added", "sid": new_id}), 201

@app.route('/students/<int:sid>', methods=['PUT'])
def update_student(sid):
    data = request.json()
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE students SET fullname=%s, course=%s, year_level=%s WHERE sid=%s;",
        (data['fullname'], data['course'], data['year_level'], sid)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Student updated"}), 200

@app.route('/students/<int:sid>', methods=['DELETE'])
def delete_student(sid):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE sid=%s;", (sid,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Student deleted"}), 200

if __name__ == '__main__':
    app.run(debug=True)

    