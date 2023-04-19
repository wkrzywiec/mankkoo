from apiflask import APIFlask
from mankkoo.controller.main_controller import main_endpoints
from mankkoo.controller.account_controller import account_endpoints
from mankkoo.util import config

app = APIFlask(__name__, title="Mankkoo - 'accounting' service API", version='1.0', spec_path='/openapi.yaml', docs_ui='elements')

app.config['SPEC_FORMAT'] = 'yaml'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

app.config['INFO'] = {
    'description': "An OpenAPI specifiaction of the Mankkoo's 'accounting' service.",
    'license': {
        'name': 'MIT License',
        'url': 'https://github.com/wkrzywiec/mankkoo/blob/main/LICENSE'
    }
}

# to enable 'prod' config first run: export FLASK_ENV=prod
if app.config["ENV"] == 'prod':
    app.config.from_object('mankkoo.config.ProdConfig')
else:
    app.config.from_object('mankkoo.config.DevConfig')

app.register_blueprint(main_endpoints, url_prefix='/api/main')
app.register_blueprint(account_endpoints, url_prefix='/api/accounts')

config.init_data_folder()