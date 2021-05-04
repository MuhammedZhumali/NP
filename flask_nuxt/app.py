import json

from flask import Flask, render_template, request, abort
from flask_restful import Api
from flask_cors import CORS  # only for debug
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/test.db'
db = SQLAlchemy(app)
CORS(app)  # only for debug


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    salary = db.Column(db.Integer)

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
    if request.method == 'GET':
        user = User.query.get(id)
        return user.serialize if user else abort(404)
    elif request.method == 'DELETE':
        user = User.query.get(id)
        if user:
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
        newUser = User(name=user["name"], salary=user["salary"])
        db.session.add(newUser)
        db.session.commit()
        return newUser.serialize
    elif request.method == 'PUT':
        req_user = json.loads(request.data)
        user = User.query.filter(User.id == req_user["id"])
        if user:
            user.update(req_user)
            db.session.commit()
            user = User.query.get(req_user["id"])
            return user.serialize
        else:
            return abort(404)


if __name__ == '__main__':
    app.run(debug=True)
