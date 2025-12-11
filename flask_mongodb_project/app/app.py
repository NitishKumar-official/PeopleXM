
from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import re

app = Flask(__name__)

# ---- MongoDB Connection ----
client = MongoClient("mongodb://localhost:27017/")
db = client["peopleXM"]
users_collection = db["user"]

#--------------------- Validation Schema ---------------
# all fields must be STRING
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

        # reject everything except pure string
        if type(value) is not str:
            return False, f"{key} must be a string only"

        # empty string not allowed
        if value.strip() == "":
            return False, f"{key} cannot be empty"

    return True, "Valid"


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

    # validate user values (not form directly)
    is_valid, msg = validate_user(user)
    if not is_valid:
        return msg, 400

    users_collection.insert_one(user)

    return redirect(url_for('show_users'))


@app.route("/users", methods=["GET"])
def get_users():
    users = list(users_collection.find({}, {"_id": 0}))
    return jsonify(users)


if __name__ == "__main__":
    app.run(debug=True, port=8000)
