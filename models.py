from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Tasks(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    prority = db.Column(db.String(50))
    deadline = db.Column(db.DateTime)
    todolist_id = db.Column(db.Integer, db.ForeignKey('todolists.id'))
    
class TodoList(db.Model):
    __tablename__ = 'todolists'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    description = db.Column(db.Text)
    tasks = db.relationship('Tasks', backref='todolist', lazy=True)

class Status(db.Model):
    __tablename__ = 'status'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.String(255))
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    tasks_relation = db.relationship('Tasks', backref='status_relation', lazy=True)

class Step(db.Model):
    __tablename__ = 'steps'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    description = db.Column(db.Text)
    order = db.Column(db.Integer)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))

class Users(db.Model):
    __tablename__= "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
