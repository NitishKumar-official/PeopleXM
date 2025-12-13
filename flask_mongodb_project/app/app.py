
from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import re
from bson.objectid import ObjectId

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

        # must be string
        if type(value) is not str:
            return False, f"{key} must be a string only"

        # empty not allowed
        if value.strip() == "":
            return False, f"{key} cannot be empty"

        # only alphabets for names
        if key in ['first_name', 'last_name']:
            if not re.match(r'^[A-Za-z]+$', value):
                return False, f"{key} must contain only alphabets"

    return True, "Valid"




#----------------------------------all routes----------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html')

#----------------------------------all data showing----------------------------------------------
@app.route('/show')
def show_users():
    users = list(users_collection.find())
    return render_template("show.html", users=users)

#-----------------------------------new user register---------------------------------------------
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


#---------------------------------------get users from database------------------------------------

@app.route("/users", methods=["GET"])
def get_users():
    users = list(users_collection.find({}, {"_id": 0}))
    return jsonify(users)

#--------------------------------------Update user details----------------------------------------
# @app.route('/user/<user_id>')
# def user_by_id():


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



#--------------------------------------Delete user details----------------------------------------
@app.route('/delete/<user_id>', methods=['POST'])
def delete_user(user_id):
    users_collection.delete_one({'_id': ObjectId(user_id)})
    return redirect(url_for('show_users'))


#--------------------------------------Update user details----------------------------------------

#---------------------------------------server live at 8000----------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=8000)
