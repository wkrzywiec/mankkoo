import os
import psycopg2
import select
import threading

from apiflask import APIFlask
from flask_cors import CORS

import mankkoo.config as app_profile
import mankkoo.database as db
import mankkoo.views as views

from mankkoo.controller.main_controller import main_endpoints
from mankkoo.controller.account_controller import account_endpoints
from mankkoo.controller.stream_controller import stream_endpoints
from mankkoo.base_logger import log
from mankkoo.config import ProdConfig, DevConfig


def create_app(app_config=None):

    if app_config is None:
        profile = os.getenv("FLASK_ENV", "prod")
        log.info(f'Starting mankkoo backend service with profile: {profile}')

        if profile == 'prod':
            app_config = ProdConfig()
        else:
            app_config = DevConfig()
    else:
        log.info(f'Starting mankkoo backend service with custom config: {app_config}')

    app = APIFlask(__name__, title="Mankkoo - 'accounting' service API", version='1.0', spec_path='/openapi.yaml', docs_ui='elements')
    CORS(app)

    app.config.from_object(app_config)

    os.environ["DB_NAME"] = app_config.DB_NAME

    app.config['SPEC_FORMAT'] = 'yaml'
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

    app.config['INFO'] = {
        'description': "An OpenAPI specifiaction of the Mankkoo's 'accounting' service.",
        'license': {
            'name': 'MIT License',
            'url': 'https://github.com/wkrzywiec/mankkoo/blob/main/LICENSE'
        }
    }

    app.register_blueprint(main_endpoints, url_prefix='/api/main')
    app.register_blueprint(account_endpoints, url_prefix='/api/accounts')
    app.register_blueprint(stream_endpoints, url_prefix='/api/streams')

    db.init_db()

    start_listener_thread()
    return app


def start_listener_thread():
    thread = threading.Thread(target=listen_to_db_notifications, daemon=True)
    thread.start()


def listen_to_db_notifications():
    log.info('Starting listening to database notifications...')

    conn = db.get_connection()
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    cursor = conn.cursor()
    cursor.execute("LISTEN events_added;")

    while True:
        if select.select([conn], [], [], 5) == ([], [], []):
            continue
        conn.poll()
        while conn.notifies:
            notify = conn.notifies.pop(0)
            handle_notification(notify)


def handle_notification(notify):
    log.info(f"Received notification. Channel: '{notify.channel}'. Payload: '{notify.payload}'")
    views.update_views(notify.payload)


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
