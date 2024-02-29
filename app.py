from flask import Flask, request
from flask_restx import Api, Resource, reqparse
from sqlalchemy import exc
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Tasks, Users, TodoList, Status
from datetime import datetime

config = Config()
app = Flask(__name__)
app.config.from_object(config)

with app.app_context():
    db.init_app(app)
    db.create_all()
    api = Api(app, version='1.0', title='Your API', description='API Description')
    api_ns = api.namespace("Reference", path='/apiv1', description="Reference Data")

    put_users_parser = reqparse.RequestParser()
    put_users_parser.add_argument('username', type=str, required=True, help='Username is required')
    put_users_parser.add_argument('password', type=str, required=True, help='Password is required')

    put_tasks_parser = reqparse.RequestParser()
    put_tasks_parser.add_argument('title', type=str, required=True, help='Title is required')
    put_tasks_parser.add_argument('description', type=str, required=True, help='Description is required')
    put_tasks_parser.add_argument('deadline', type=str, required=True, help='Deadline is required')
    put_tasks_parser.add_argument('prority', type=str, required=True, help='prority is required')
    # put_tasks_parser.add_argument('status', type=str, required=True, help='Status is required')
    put_tasks_parser.add_argument('todolist_id', type=int, required=True, help='TodoList ID is required')

    put_todolist_parser = reqparse.RequestParser()
    put_todolist_parser.add_argument('name', type=str, required=True, help='Name is required')
    put_todolist_parser.add_argument('description', type=str, required=True, help='Description is required')

    put_task_update_parser = reqparse.RequestParser()
    put_task_update_parser.add_argument('title', type=str, required=False, help='Title is required')
    put_task_update_parser.add_argument('description', type=str, required=False, help='Description is required')
    put_task_update_parser.add_argument('deadline', type=str, required=False, help='Deadline is required')
    put_task_update_parser.add_argument('todolist_id', type=int, required=False, help='TodoList ID is required')
    # put_task_update_parser.add_argument('status', type=str, required=False, help='Status of the task')
    put_task_update_parser.add_argument('completion_date', type=str, required=False, help='Completion date of the task')

    put_status_update_parser = reqparse.RequestParser()
    put_status_update_parser.add_argument('status', type=str, required=False, help='Status is required')
    put_status_update_parser.add_argument('task_id', type=int, required=False, help='Task ID is required')

@api_ns.route('/status/<int:id>')
class UpdateStatus(Resource):
    @api.expect(put_status_update_parser)
    def put(self, id):
        # Attempt to get the status with the given id
        status = Status.query.get(id)

        # If the status doesn't exist, create a new instance
        if not status:
            status = Status(id=id)

        args = put_status_update_parser.parse_args()

        if 'status' in args and args['status'] is not None:
            status.status = args['status']
        if 'task_id' in args and args['task_id'] is not None:
            task = Tasks.query.get(args['task_id'])
            if not task:
                return {'message': 'Task not found'}, 404
            status.task_id = args['task_id']

        try:
            db.session.add(status)  # Add the status instance to the session
            db.session.commit()
            return {'message': 'Status updated successfully'}, 200
        except exc.SQLAlchemyError:
            db.session.rollback()
            return {'message': 'Failed to update status'}, 500
        
    @api.expect(put_status_update_parser)
    def post(self, id):
        args = put_status_update_parser.parse_args()

        if 'status' not in args or args['status'] is None:
            return {'message': 'Status is required for creating a new status'}, 400
        new_status = Status(id=id, status=args['status'])

        if 'task_id' in args and args['task_id'] is not None:
            task = Tasks.query.get(args['task_id'])
            if not task:
                return {'message': 'Task not found'}, 404
            new_status.task_id = args['task_id']

        try:
            db.session.add(new_status)  # Add the new status instance to the session
            db.session.commit()
            return {'message': 'New status created successfully'}, 201
        except exc.SQLAlchemyError:
            db.session.rollback()
            return {'message': 'Failed to create new status'}, 500


@api_ns.route('/tasks/<int:id>')



@api_ns.route('/tasks/<int:id>')
class TaskResource(Resource):
    def get(self, id):
        task = Tasks.query.get(id)

        if not task:
            return {'message': 'Task not found'}, 404

        if not isinstance(task.deadline, datetime):
            deadline_str = "Invalid Deadline"
        else:
            deadline_str = task.deadline.strftime("%Y-%m-%dT%H:%M:%S")

        task_data = {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'deadline': deadline_str,
            'prority': task.prority,
            'todolist_id': task.todolist_id
        }

        return {'task': task_data}, 200 

    def delete(self, id):
        task = Tasks.query.get(id)

        if not task:
            return {'message': 'Task not found'}, 404

        db.session.delete(task)

        return {'message': 'Task deleted successfully'}, 200
    
    @api.expect(put_task_update_parser)
    def put(self, id):
        task = Tasks.query.get(id)

        if not task:
            return {'message': 'Task not found'}, 404

        args = put_task_update_parser.parse_args()

        if 'title' in args and args['title'] is not None:
            task.title = args['title']
        if 'description' in args and args['description'] is not None:
            task.description = args['description']
        if 'deadline' in args and args['deadline'] is not None:
            try:
                task.deadline = datetime.strptime(args['deadline'], "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                return {'message': 'Invalid deadline format. Use YYYY-MM-DDTHH:%M:%S'}, 400
        if 'todolist_id' in args and args['todolist_id'] is not None:
            todolist = TodoList.query.get(args['todolist_id'])
            if not todolist:
                return {'message': 'TodoList not found'}, 404
            task.todolist_id = args['todolist_id']
        if 'completion_date' in args and args['completion_date'] is not None:
            try:
                task.completion_date = datetime.strptime(args['completion_date'], "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                return {'message': 'Invalid completion date format. Use YYYY-MM-DDTHH:%M:%S'}, 400

        try:
            db.session.commit()
            return {'message': 'Task updated successfully'}, 200
        except exc.SQLAlchemyError:
            db.session.rollback()
            return {'message': 'Failed to update task'}, 500
        

@api_ns.route('/todolists/<int:id>/tasks')
class TodoListTasksResource(Resource):
    def get(self, id):
        todolist = TodoList.query.get(id)
        if not todolist:
            return {'message': 'TodoList not found'}, 404

        tasks = Tasks.query.filter_by(todolist_id=id).all()

        task_list = []

        for task in tasks:
            if not isinstance(task.deadline, datetime):
                deadline_str = "Invalid Deadline"
            else:
                deadline_str = task.deadline.strftime("%Y-%m-%dT%H:%M:%S")

            task_data = {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'deadline': deadline_str,
                'prority': task.prority,
                'todolist_id': task.todolist_id
            }

            task_list.append(task_data)

        return {'tasks': task_list}, 200

@api_ns.route('/todolists')
class TodoListResource(Resource):
    @api.expect(put_todolist_parser)
    def post(self):
        args = put_todolist_parser.parse_args()
        name = args['name']
        description = args['description']

        new_todolist = TodoList(name=name, description=description)
        db.session.add(new_todolist)

        try:
            db.session.commit()
            return {'message': 'TodoList created successfully'}, 201
        except exc.SQLAlchemyError:
            db.session.rollback()
            return {'message': 'Failed to create TodoList'}, 500

@api_ns.route('/tasks')
class TaskList(Resource):
    @api.expect(put_tasks_parser)
    def post(self):
        args = put_tasks_parser.parse_args()
        title = args['title']
        description = args['description']
        deadline_str = args['deadline']  # Get deadline as a string
        prority = args['prority']
        todolist_id = args['todolist_id']

        todolist = TodoList.query.get(todolist_id)
        if not todolist:
            return {'message': 'TodoList not found'}, 404

        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%dT%H:%M:%S")

            task = Tasks(title=title, description=description, deadline=deadline, prority=prority, todolist_id=todolist_id)
            db.session.add(task)
            db.session.commit()

            return {'message': 'Task created successfully'}, 201
        except ValueError:
            return {'message': 'Invalid deadline format. Use YYYY-MM-DDTH:S:%M:%S'}, 400

    def get(self):
        status = request.args.get('status')
        if status:
            tasks = Tasks.query.filter_by(status=status).all()
        else:
            tasks = Tasks.query.all()

        task_list = []

        for task in tasks:
            if not isinstance(task.deadline, datetime):
                deadline_str = "Invalid Deadline"
            else:
                deadline_str = task.deadline.strftime("%Y-%m-%dT%H:%M:%S")

            task_data = {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'deadline': deadline_str,
                'prority': task.prority,
                'todolist_id': task.todolist_id
            }

            task_list.append(task_data)

        return {'tasks': task_list}, 200


@api.route('/swagger')
class SwaggerResource(Resource):
    def get(self):
        return api.swagger_ui()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)

