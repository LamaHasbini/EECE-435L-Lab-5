from flask import Flask, request, jsonify #added to top of file
from flask_cors import CORS #added to top of file
import database
import sqlite3

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/api/users', methods=['GET'])
def api_get_users():
    return jsonify(database.get_users())

@app.route('/api/users/<user_id>', methods=['GET'])

def api_get_user(user_id):
    return jsonify(database.get_user_by_id(user_id))

@app.route('/api/users/add', methods = ['POST'])
def api_add_user():
    user = request.get_json()
    return jsonify(database.insert_user(user))

@app.route('/api/users/update', methods = ['PUT'])
def api_update_user():
    user = request.get_json()
    return jsonify(database.update_user(user))

@app.route('/api/users/delete/<user_id>', methods = ['DELETE'])
def api_delete_user(user_id):
    return jsonify(database.delete_user(user_id))

@app.route('/api/users/update/<user_id>', methods=['PATCH'])
def api_patch_user(user_id):
    user_data = request.get_json()
    updated_user = {}
    
    try:
        conn = database.connect_to_db()
        conn.row_factory = sqlite3.Row  
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        existing_user = cur.fetchone()

        if existing_user:
            name = user_data.get("name", existing_user["name"])
            email = user_data.get("email", existing_user["email"])
            phone = user_data.get("phone", existing_user["phone"])
            address = user_data.get("address", existing_user["address"])
            country = user_data.get("country", existing_user["country"])
            
            cur.execute("""
                UPDATE users 
                SET name = ?, email = ?, phone = ?, address = ?, country = ?
                WHERE user_id = ?
            """, (name, email, phone, address, country, user_id))

            conn.commit()
            
            updated_user = database.get_user_by_id(user_id)
        else:
            return jsonify({"error": "User not found"}), 404
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
    
    return jsonify(updated_user), 200

if __name__ == "__main__":
    #app.debug = True
    #app.run(debug=True)
    database.connect_to_db()
    database.create_db_table()
    app.run() #run app