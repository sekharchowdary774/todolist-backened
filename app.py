from flask import Flask, request, jsonify

from flask_cors import CORS
import db

app = Flask(__name__)
CORS(app)

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    conn = db.get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, password)
        )
        conn.commit()
        return jsonify({"message": "Registration successful"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()
@app.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"success": False, "error": "Email required"}), 400

    # Instead of sending real email, just generate a reset link
    reset_link = f"http://localhost:3000/reset/{email}"

    # Respond with the link
    return jsonify({"success": True, "reset_link": reset_link, "message": "Use this link to reset your password"})
# ✅ Update password after reset
@app.route("/update-password", methods=["POST"])
def update_password():
    data = request.get_json()
    email = data.get("email")
    new_password = data.get("password")

    if not email or not new_password:
        return jsonify({"success": False, "error": "Email and password required"}), 400

    conn = db.get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE users SET password=%s WHERE email=%s", (new_password, email))
        conn.commit()

        if cursor.rowcount == 0:  # no user with that email
            return jsonify({"success": False, "error": "User not found"}), 404

        return jsonify({"success": True, "message": "Password updated successfully"})
    finally:
        cursor.close()
        conn.close()

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)  # return dict instead of tuple

    try:
        cursor.execute(
            "SELECT id, username, email FROM users WHERE username = %s AND password = %s",
            (username, password)
        )
        user = cursor.fetchone()
        print("Login attempt:", username, password)
        print("DB user:", user)

        if user:
            return jsonify({
                "success": True,
                "message": "Login successful",
                "user": user
            })
        else:
            return jsonify({"success": False, "error": "Invalid credentials"}), 401
    finally:
        cursor.close()
        conn.close()

# ✅ Update user (username or password)
@app.route("/update_user/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.json
    new_username = data.get("username")
    new_password = data.get("password")

    conn = db.get_db_connection()
    cursor = conn.cursor()

    try:
        if new_username and new_password:
            cursor.execute(
                "UPDATE users SET username=%s, password=%s WHERE id=%s",
                (new_username, new_password, user_id)
            )
        elif new_username:
            cursor.execute(
                "UPDATE users SET username=%s WHERE id=%s",
                (new_username, user_id)
            )
        elif new_password:
            cursor.execute(
                "UPDATE users SET password=%s WHERE id=%s",
                (new_password, user_id)
            )
        else:
            return jsonify({"error": "No fields to update"}), 400

        conn.commit()
        return jsonify({"success": True, "message": "User updated"})
    finally:
        cursor.close()
        conn.close()


# ✅ Delete user
@app.route("/delete_user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    conn = db.get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
        conn.commit()
        return jsonify({"success": True, "message": "User deleted"})
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)
    
