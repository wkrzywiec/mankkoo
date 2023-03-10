from apiflask import APIFlask
from accounting.controller.main_controller import main_endpoints
from accounting.controller.account_controller import account_endpoints

app = APIFlask(__name__, title='Mankkoo API', version='1.0', spec_path='/openapi.yaml')

app.config['SPEC_FORMAT'] = 'yaml'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# to enable 'prod' config first run: export FLASK_ENV=prod
if app.config["ENV"] == 'prod':
    app.config.from_object('accounting.config.ProdConfig')
else:
    app.config.from_object('accounting.config.DevConfig')

app.register_blueprint(main_endpoints, url_prefix='/api/main')
app.register_blueprint(account_endpoints, url_prefix='/api/accounts')