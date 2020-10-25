from .api import app
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import ForeignKey
from passlib.apps import custom_app_context as pwd_context
import datetime
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'postgres://rashvrmhpzbczi:fe846f1cd0f3d944c3c96d3f3e1f8b89658968f4074e2f005525742265b81a5d@ec2-54-217-206-236.eu-west-1.compute.amazonaws.com:5432/dehckj186cusnb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "sdfsdfdfs"
db = SQLAlchemy(app)
ma = Marshmallow(app)


class users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(12), unique=True, nullable=True)
    create_date = db.Column(db.Date, nullable=False)
    edit_date = db.Column(db.Date, nullable=True)
    access_level = db.Column(db.Boolean, nullable=False)

    def verify_pass(self, password):
        return pwd_context.verify(password, self.password)

    def generate_auth_token(self, expiration=3600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    def get_role(self):
        return self.access_level

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        user = users.query.get(data['id'])
        return user

    def __init__(self, email, password, phone, access_level):
        self.create_date = datetime.datetime.now()
        self.email = email
        self.password = pwd_context.encrypt(password)
        self.phone = phone
        if access_level == '1':
            self.access_level = True
        else:
            self.access_level = False

    def __repr__(self):
        return "id : {0}, email : {1}, password : {2}, access_level : {3}". \
            format(self.id, self.email, self.password, self.access_level)


class test_results(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    result = db.Column(db.Integer, nullable=True)
    test_id = db.Column(db.Integer, ForeignKey('tests.id'), nullable=False)

    def __init__(self, user_id):
        self.user_id = user_id
        self.start_date = datetime.datetime.now()

    def __repr__(self):
        return "id : {0}, user_id : {1}, start_date : {2}, end_date : {3}, result : {4}". \
            format(self.id, self.user_id, self.start_date, self.end_date, self.result)


class test_subject(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "id : {0}, name : {1}". \
            format(self.id, self.name)


class tests(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    test_subject_id = db.Column(db.Integer, ForeignKey('test_subject.id'), nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    create_date = db.Column(db.Date, nullable=False)
    edit_date = db.Column(db.Date, nullable=True)

    def __init__(self, test_subject_id, name):
        self.name = name
        self.test_subject_id = test_subject_id
        self.create_date = datetime.datetime.now()

    def __repr__(self):
        return "id : {0}, name : {1}". \
            format(self.id, self.name)


class question_type(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "id : {0}, name : {1}". \
            format(self.id, self.name)


class questions(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    test_id = db.Column(db.Integer, ForeignKey('tests.id'), nullable=False)
    question_type_id = db.Column(db.Integer, ForeignKey('question_type.id'), nullable=False)
    question = db.Column(db.String(50), unique=True, nullable=False)
    create_date = db.Column(db.Date, nullable=False)
    edit_date = db.Column(db.Date, nullable=True)

    def __init__(self, test_id, question_type_id, question):
        self.test_id = test_id
        self.question_type_id = question_type_id
        self.question = question
        self.create_date = datetime.datetime.now()

    def __repr__(self):
        return "id : {0}, test_id : {1}, question_type_id : {2}, question : {3}, create_date : {4}, edit_date : {5} ". \
            format(self.id, self.test_id, self.question_type_id, self.question, self.create_date, self.edit_date)


class answers(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    answer = db.Column(db.String(50), unique=True, nullable=False)

    def __init__(self, answer):
        self.answer = answer

    def __repr__(self):
        return "id : {0}, answer : {1}". \
            format(self.id, self.answer)


class question_answer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(db.Integer, ForeignKey('questions.id'), nullable=False)
    answer_id = db.Column(db.Integer, ForeignKey('answers.id'), nullable=False)
    is_right = db.Column(db.Boolean, nullable=False)

    def __init__(self, question_id, answer_id, is_right):
        self.question_id = question_id
        self.answer_id = answer_id
        self.is_right = is_right

    def __repr__(self):
        return "id : {0}, question_id : {1}, answer_id : {2}, is_right : {3}". \
            format(self.id, self.question_id, self.answer_id, self.is_right)


class users_answers(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    question_answer_id = db.Column(db.Integer, ForeignKey('question_answer.id'), nullable=False)

    def __init__(self, user_id, question_answer_id):
        self.user_id = user_id
        self.question_answer_id = question_answer_id

    def __repr__(self):
        return "id : {0}, user_id : {1}, question_answer_id : {2}". \
            format(self.id, self.user_id, self.question_answer_id)


class user_schema(ma.Schema):
    class Meta:
        fields = ("id", "email", "password", "phone", "create_date", "edit_date", "access_level")


class subject_schema(ma.Schema):
    class Meta:
        fields = ("id", "name", "description")


subjects_schema = subject_schema(many=True)
subject_schema = subject_schema()

users_schema = user_schema(many=True)
user_schema = user_schema()
