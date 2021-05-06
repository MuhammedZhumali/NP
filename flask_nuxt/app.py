import json

from flask import Flask, render_template, request, abort
from flask_restful import Api
from flask_cors import CORS  # only for debug
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/test.db'
db = SQLAlchemy(app)
CORS(app)  # only for debug


class User(db.Model):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    salary = db.Column(db.Integer)
    messages = relationship("Message")
    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name,
            'salary': self.salary
        }

    def __repr__(self):
        return '<User %r>' % self.name

class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100))
    user_id = db.Column(
        db.Integer,
        ForeignKey('Users.id', ondelete='CASCADE'),
        nullable=False,
    )

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'content': self.content,
            'user_id' : self.user_id
        }

    def __repr__(self):
        return '<Message %r>' % self.name

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404


@app.route('/<page>')
def send_html(page):
    return app.send_static_file('%s/index.html' % page)


@app.route('/')
def send_main_html():
    return app.send_static_file('index.html')


@app.route('/api/user/<int:id>', methods=['GET', 'DELETE'])
def user(id):
    user = User.query.get(id)
    if request.method == 'GET':
        if user != None:
            return user.serialize
        else:
            return abort(404)
    elif request.method == 'DELETE':
        if user != None:
            db.session.delete(user)
            db.session.commit()
            return user.serialize
        else:
            return abort(404)


@app.route('/api/user', methods=['GET', 'POST', 'PUT'])
def get_users():
    if request.method == 'GET':
        return json.dumps([i.serialize for i in User.query.all()])
    elif request.method == 'POST':
        user = json.loads(request.data)
        newUser = User(name=user["name"],salary=user["salary"])
        db.session.add(newUser)
        db.session.commit()
        return newUser.serialize
    elif request.method == 'PUT':
        user = json.loads(request.data)
        newUser = User.query.filter(User.id == user["id"])
        if newUser != None:
            newUser.update(user)
            db.session.commit()
            user = User.query.get(user["id"])
            return user.serialize
        else:
            return abort(404)


@app.route('/api/message', methods=['GET', 'POST', 'PUT'])
def get_messages():
    if request.method == 'GET':
        return json.dumps([i.serialize for i in Message.query.all()])
    # elif request.method == 'POST':
    #     message = json.loads(request.data)
    #     newUser = User(name=user["name"],salary=user["salary"])
    #     db.session.add(newUser)
    #     db.session.commit()
    #     return newUser.serialize
    # elif request.method == 'PUT':
    #     user = json.loads(request.data)
    #     newUser = User.query.filter(User.id == user["id"])
    #     if newUser != None:
    #         newUser.update(user)
    #         db.session.commit()
    #         user = User.query.get(user["id"])
    #         return user.serialize
    #     else:
    #         return abort(404)


@app.route('/api/message/<int:user_id>', methods=['GET'])
def getUserMessages(user_id):
    if request.method == 'GET':
        user = User.query.get(user_id)
        if user:
            return json.dumps([i.serialize for i in user.messages])
        else:
            return abort(404)

if __name__ == '__main__':
    app.run(debug=True)