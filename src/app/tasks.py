import flask
from flask import request, current_app

from .db.models import Task

blueprint = flask.Blueprint("tasks", __name__)


@blueprint.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.select()
    return flask.jsonify({
        "data": [task.to_response(flask.request.base_url) for task in tasks]
    })


@blueprint.route('/tasks', methods=['POST'])
def create_task():
    if "data" not in flask.request.json:
        return flask.jsonify({"message": "data is required"}), 400

    if "attributes" not in flask.request.json["data"]:
        return flask.jsonify({"message": "data.attributes is required"}), 400

    if "title" not in flask.request.json["data"]["attributes"]:
        return flask.jsonify({"message": "data.attributes.title is required"}), 400

    tasks_total_count = Task.select().count()
    if tasks_total_count >= current_app.config['MAX_TASKS_COUNT']:
        return flask.jsonify({"message": "Max tasks number exceeded"}), 400

    task = Task.create(
        title=flask.request.json["data"]["attributes"]["title"],
        command=flask.request.json["data"]["attributes"]["command"],
        image=flask.request.json["data"]["attributes"]["image"],
        description=flask.request.json["data"]["attributes"]["description"],
    )

    return flask.jsonify({"data": task.to_response(flask.request.base_url)}), 201


@blueprint.route('/tasks/<int:id_>', methods=['GET'])
def get_task_by_id(id_: int):
    task = Task.get_or_none(id_)

    if not task:
        return flask.jsonify({"message": "Task not found"}), 404

    return flask.jsonify({"data": task.to_response(flask.request.base_url)}), 200


@blueprint.route('/tasks/<int:id_>', methods=['PATCH'])
def update_task_by_id(id_: int):
    task = Task.get_or_none(id_)

    if not task:
        return flask.jsonify({"message": "Task not found"}), 404

    body = request.get_json()
    task.update(**body).execute()

    return flask.jsonify({"data": task.to_response(flask.request.base_url)}), 200


@blueprint.route('/tasks/<int:id_>', methods=['DELETE'])
def delete_task_by_id(id_: int):
    task = Task.get_or_none(id_)

    if not task:
        return flask.jsonify({"message": "Task not found"}), 404

    if task.status == Task.Status.running:
        return flask.jsonify({"message": "Task is running"}), 400

    task.delete_instance()

    return '', 204


@blueprint.route('/tasks/<int:id_>/logs', methods=['GET'])
def get_task_logs_by_id(id_: int):
    task = Task.get_or_none(id_)

    if not task:
        return flask.jsonify({"message": "Task not found"}), 404

    return flask.jsonify({"data": task.logs}), 200
