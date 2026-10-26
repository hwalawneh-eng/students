
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="students"
    )


@app.route("/")
def home():
    return render_template("StudentFrontend.html")


# Check database connection and data
@app.route("/api/db-check", methods=["GET"])
def db_check():
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT DATABASE() AS db_name")
        database = cursor.fetchone()

        cursor.execute(
            "SELECT id, name, email, phone, gender FROM stu"
        )
        students = cursor.fetchall()

        return jsonify({
            "database": database,
            "students": students
        })

    except mysql.connector.Error:
        app.logger.exception("Database check failed")
        return jsonify({"error": "Database check failed"}), 500

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


# Get all students
@app.route("/api/students", methods=["GET"])
def get_students():
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT id, name, email, phone, gender FROM stu"
        )
        return jsonify(cursor.fetchall())

    except mysql.connector.Error:
        app.logger.exception("Failed to fetch students")
        return jsonify({"error": "Failed to fetch students"}), 500

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


# Get one student
@app.route("/api/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT id, name, email, phone, gender FROM stu WHERE id = %s",
            (student_id,)
        )
        student = cursor.fetchone()

        if student is None:
            return jsonify({"error": "Student not found"}), 404

        return jsonify(student), 200

    except mysql.connector.Error:
        app.logger.exception("Failed to fetch student")
        return jsonify({"error": "Failed to fetch student"}), 500

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


# Add a student
@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    phone = str(data.get("phone", "")).strip()
    gender = str(data.get("gender", "")).strip()

    if not all([name, email, phone, gender]):
        return jsonify({"error": "All fields are required"}), 400

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO stu (name, email, phone, gender) "
            "VALUES (%s, %s, %s, %s)",
            (name, email, phone, gender)
        )
        connection.commit()

        return jsonify({
            "message": "Student added successfully",
            "id": cursor.lastrowid
        }), 201

    except mysql.connector.Error:
        app.logger.exception("Failed to add student")
        if connection is not None:
            connection.rollback()
        return jsonify({"error": "Failed to add student"}), 500

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


# Update a student
@app.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    phone = str(data.get("phone", "")).strip()
    gender = str(data.get("gender", "")).strip()

    if not all([name, email, phone, gender]):
        return jsonify({"error": "All fields are required"}), 400

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "UPDATE stu SET name=%s, email=%s, phone=%s, gender=%s "
            "WHERE id=%s",
            (name, email, phone, gender, student_id)
        )
        connection.commit()

        if cursor.rowcount == 0:
            cursor.execute(
                "SELECT id FROM stu WHERE id=%s",
                (student_id,)
            )
            if cursor.fetchone() is None:
                return jsonify({"error": "Student not found"}), 404

        return jsonify({"message": "Student updated successfully"})

    except mysql.connector.Error:
        app.logger.exception("Failed to update student")
        if connection is not None:
            connection.rollback()
        return jsonify({"error": "Failed to update student"}), 500

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


# Delete a student
@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM stu WHERE id=%s",
            (student_id,)
        )
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Student not found"}), 404

        return jsonify({"message": "Student deleted successfully"})

    except mysql.connector.Error:
        app.logger.exception("Failed to delete student")
        if connection is not None:
            connection.rollback()
        return jsonify({"error": "Failed to delete student"}), 500

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
