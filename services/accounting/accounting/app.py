from flask import Flask
from accounting.controller.main_controller import main

app = Flask(__name__)
app.register_blueprint(main, url_prefix='/api/main')