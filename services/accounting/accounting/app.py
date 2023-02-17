from flask import Flask
from accounting.controller.main_controller import main_endpoints
from accounting.controller.account_controller import account_endpoints

app = Flask(__name__)

# to enable 'prod' config first run: export FLASK_ENV=prod
if app.config["ENV"] == 'prod':
    app.config.from_object('accounting.config.ProdConfig')
else:
    app.config.from_object('accounting.config.DevConfig')

app.register_blueprint(main_endpoints, url_prefix='/api/main')
app.register_blueprint(account_endpoints, url_prefix='/api/accounts')