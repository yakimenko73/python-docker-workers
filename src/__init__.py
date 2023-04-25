from typing import Final

import docker
import flask
import swagger_ui

from src import db, tasks

docker_client = docker.from_env()

API_SPEC_PATH: Final[str] = './static/openapi.yaml'


def init_app():
    app = flask.Flask(__name__)
    app.register_blueprint(tasks.blueprint)
    app.add_url_rule('/', endpoint='bp_docs.swagger_blueprint_doc_handler')

    swagger_ui.api_doc(app, config_path=API_SPEC_PATH, title='API doc', url_prefix='/docs')

    return app
