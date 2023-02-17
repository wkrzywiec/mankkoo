from flask import Flask
from accounting.controller.main_controller import main

app = Flask(__name__)

# to enable 'prod' config first run: export FLASK_ENV=prod
if app.config["ENV"] == 'prod':
    app.config.from_object('accounting.config.ProdConfig')
else:
    app.config.from_object('accounting.config.DevConfig')

app.register_blueprint(main, url_prefix='/api/main')