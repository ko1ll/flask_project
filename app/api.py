from flask import Flask, request, jsonify, abort
from flask_httpauth import HTTPBasicAuth
import re
from mods import *
from passlib import pwd

app = Flask(__name__)
auth = HTTPBasicAuth()


@auth.get_user_roles
def get_user_roles(user):
    return users.user.get_role()


@auth.verify_password
def verify_password(username_or_token, password):
    user = users.verify_auth_token(username_or_token)
    if not user:
        user = users.query.filter_by(email=username_or_token).first()
        if not user or not user.verify_pass(password):
            return False
    users.user = user
    return True


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = users.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


@app.route("/api/subject", methods=['POST'])
@auth.login_required(role=True)
def add_subject():
    name = request.json['name']

    subject = test_subject(name)
    db.session.add(subject)
    db.session.commit()

    return subject_schema.jsonify(subject)


@app.route("/api/subject", methods=['GET'])
@auth.login_required(role=[False, True])
def get_subject():
    all_subjects = test_subject.query.all()
    result = subjects_schema.dump(all_subjects)
    return jsonify(result)


@app.route('/api/users', methods=['POST'])
@auth.login_required(role=True)
def new_user():
    email = request.json['email']
    phone = request.json['phone']
    access_level = request.json['access_level']
    if email is None:
        abort(400, "Null email")
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        abort(400, "Wrong email")
    if users.query.filter_by(email=email).first() is not None \
            or users.query.filter_by(phone=phone).first() is not None:
        abort(400, "Email or Phone alrdy exits")
    password = pwd.genword()
    user = users(email, password, phone, access_level)
    db.session.add(user)
    db.session.commit()
    return jsonify(password)

