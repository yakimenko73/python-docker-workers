from typing import Final

import flask
import swagger_ui

from . import tasks

API_SPEC_PATH: Final[str] = './static/openapi.yaml'
MAX_TASKS_COUNT: Final[int] = 100


def create():
    app = flask.Flask(__name__)
    app.register_blueprint(tasks.blueprint)
    app.add_url_rule('/', endpoint='bp_docs.swagger_blueprint_doc_handler')

    swagger_ui.api_doc(app, config_path=API_SPEC_PATH, title='API doc', url_prefix='/docs')

    app.config['MAX_TASKS_COUNT'] = MAX_TASKS_COUNT

    return app
