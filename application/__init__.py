from flask import Flask
from config import Config
from flask_mongoengine import MongoEngine
from flask_bootstrap import Bootstrap
app = Flask(__name__)
Bootstrap(app)

app.config.from_object(Config)

db = MongoEngine()
db.init_app(app)

from application import routes

