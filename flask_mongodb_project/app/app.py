
from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import re
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
application = app   # for deployment (Render / Gunicorn)

# ---- MongoDB Connection ----
client = MongoClient(os.getenv("MONGO_URI"))
db = client["peopleXM"]
users_collection = db["user"]

# ------------------ Validation Schema ------------------
user_schema = {
    "first_name": str,
    "last_name": str,
    "email": str
}

def validate_user(data):
    for key in user_schema.keys():

        if key not in data:
            return False, f"{key} is missing"

        value = data[key]

        if type(value) is not str:
            return False, f"{key} must be a string only"

        if value.strip() == "":
            return False, f"{key} cannot be empty"

        if key in ['first_name', 'last_name']:
            if not re.match(r'^[A-Za-z]+$', value):
                return False, f"{key} must contain only alphabets"

    return True, "Valid"

# ------------------ Routes ------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/show')
def show_users():
    users = list(users_collection.find())
    return render_template("show.html", users=users)

@app.route('/user', methods=['POST'])
def add_user():
    data = request.form

    user = {
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "email": data.get("email")
    }

    is_valid, msg = validate_user(user)
    if not is_valid:
        return msg, 400

    users_collection.insert_one(user)
    return redirect(url_for('show_users'))

@app.route("/users", methods=["GET"])
def get_users():
    users = list(users_collection.find({}, {"_id": 0}))
    return jsonify(users)

@app.route('/user/<user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    user = users_collection.find_one({'_id': ObjectId(user_id)})

    if request.method == 'POST':
        updated_data = {
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'email': request.form.get('email')
        }

        is_valid, msg = validate_user(updated_data)
        if not is_valid:
            return msg, 400

        users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': updated_data}
        )

        return redirect(url_for('show_users'))

    return render_template('update_user.html', user=user)

@app.route('/delete/<user_id>', methods=['POST'])
def delete_user(user_id):
    users_collection.delete_one({'_id': ObjectId(user_id)})
    return redirect(url_for('show_users'))

# ------------------ Run Server ------------------
if __name__ == "__main__":
    app.run(debug=True, port=8000)






#mongodb+srv://kumarnitish27212_db_user:NvRLBnXYtd8kAA5V@cluster0.efvfnzn.mongodb.net/?appName=Cluster0