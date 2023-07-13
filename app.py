from flask import Flask, make_response, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS


# flask app instance
app = Flask(__name__)
# marshmallow instance
ma = Marshmallow(app)
# Using SQLite Database
db = SQLAlchemy()
# configure the SQLite database # creating database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
# initialize the app with the extension
db.init_app(app)
# For Cors Policy
CORS(app)

# User Model


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    createdAt = db.Column(
        db.DateTime, server_default=db.func.now(), nullable=False)
    updatedAt = db.Column(db.DateTime, server_default=db.func.now(),
                          onupdate=db.func.now(), nullable=False)

    # overwriting dunder method
    def __repr__(self) -> str:
        return f'{self.name}'

# For serialize into readable json to front-end


class UserSchema(ma.Schema):
    class Meta:
        # expose fields to be serialize
        fields = ('id', 'name', 'email', 'phone')


user_schema = UserSchema()  # one row
users_schema = UserSchema(many=True)  # multiple rows

# # create database first time
# with app.app_context():
#     db.create_all()

HOST_URL = 'http://localhost:5000'


# Home Route


@app.route("/", methods=['GET'])
def index():
    return make_response(jsonify({"msg": "welcome to user management api"}))

# Get all users data, add a new user


@app.route("/users", methods=['GET', 'POST'])
def get():
    if request.method == 'GET':
        try:
            allUsers = db.session.execute(
                db.select(Users).order_by(Users.createdAt)).scalars()
            # .createdAt.desc() for reverse
            users = users_schema.dump(allUsers)
            return make_response(jsonify({"users": users}))
        except Exception as e:
            return make_response(jsonify({'status': 'error', "error": str(e.__dict__['orig'])}))

    if request.method == "POST":
        try:
            obj = request.get_json()
            user = Users(name=obj['name'],
                         email=obj['email'], phone=obj['phone'])

            db.session.add(user)
            db.session.commit()
            return make_response(jsonify({'status': 'ok', 'msg': 'user added sucessfully'}))
        except Exception as e:

            # print(e.__class__.__name__)
            # print(e.__dict__)

            return make_response(jsonify({'status': 'error', "error": str(e.__dict__['orig'])}))


# get, update, delete data of single user
@app.route("/users/<int:id>", methods=['GET', 'PUT', 'DELETE'])
def get_one(id):
    if request.method == "GET":
        try:
            user = db.session.execute(
                db.select(Users).filter_by(id=int(id))).scalar_one()
            res = user_schema.dump(user)
            return make_response(jsonify({'user': res}))
        except Exception as e:
            return make_response(jsonify({"status": "error", "error": str(e.__dict__['orig'])}))

    if request.method == "PUT":
        try:
            obj = request.get_json()
            user = db.session.execute(
                db.select(Users).filter_by(id=id)).scalar_one()
            user.name = obj['name']
            user.email = obj['email']
            user.phone = obj['phone']

            db.session.add(user)
            db.session.commit()
            return make_response(jsonify({'status': 'ok', 'msg': 'Updated sucessfully'}))
        except Exception as e:
            return make_response(jsonify({'status': 'error', "error": str(e.__dict__['orig'])}))

    if request.method == "DELETE":
        try:
            user = db.session.execute(
                db.select(Users).filter_by(id=id)).scalar_one()
            db.session.delete(user)
            db.session.commit()
            return make_response(jsonify({'status': 'ok', 'msg': 'deletion success'}))
        except Exception as e:
            return make_response(jsonify({'status': 'error', "error": str(e.__dict__['orig'])}))


# staring the flask server on custom socket
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
