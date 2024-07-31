import os

from apiflask import APIFlask
from flask_cors import CORS

from mankkoo.controller.main_controller import main_endpoints
from mankkoo.controller.account_controller import account_endpoints
from mankkoo.util import config
from mankkoo.base_logger import log
import mankkoo.config as app_profile
import mankkoo.database as db


app = APIFlask(__name__, title="Mankkoo - 'accounting' service API", version='1.0', spec_path='/openapi.yaml', docs_ui='elements')
CORS(app)

app.config['SPEC_FORMAT'] = 'yaml'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

app.config['INFO'] = {
    'description': "An OpenAPI specifiaction of the Mankkoo's 'accounting' service.",
    'license': {
        'name': 'MIT License',
        'url': 'https://github.com/wkrzywiec/mankkoo/blob/main/LICENSE'
    }
}

db_name = ''

# to enable 'prod' config first run: export FLASK_ENV=prod
app.config["ENV"] = os.getenv("FLASK_ENV", "dev")
log.info(f'Starting mankkoo backend service with profile: {app.config["ENV"]}')

if app.config["ENV"] == 'prod':
    app.config.from_object('mankkoo.config.ProdConfig')
    db_name = app_profile.ProdConfig.DB_NAME
else:
    app.config.from_object('mankkoo.config.DevConfig')
    db_name = app_profile.DevConfig.DB_NAME

app.register_blueprint(main_endpoints, url_prefix='/api/main')
app.register_blueprint(account_endpoints, url_prefix='/api/accounts')

os.environ["DB_NAME"] = db_name
db.init_db()

config.init_data_folder()
