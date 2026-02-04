# routes/user.py
from flask import Blueprint, jsonify
from db.database_connect import get_db_connection

user_bp = Blueprint("user", __name__)

# routes/user.py
@user_bp.route("/api/users")
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.id, u.username
        FROM users u
        WHERE EXISTS (
            SELECT 1 FROM user_guardians ug WHERE ug.user_id = u.id
        )
        ORDER BY u.id
    """)
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users)

@user_bp.route("/api/guardians/<int:user_id>")
def get_guardians(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.username, u.phone_number
        FROM user_guardians ug
        JOIN users u ON ug.guardian_id = u.id
        WHERE ug.user_id = %s
    """, (user_id,))
    guardians = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(guardians)
