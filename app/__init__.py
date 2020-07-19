from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_whooshee import Whooshee

app = Flask(__name__)
app.config.from_object(Config)
app.config['WHOOSH_BASE'] = "."
db = SQLAlchemy(app)
migrate = Migrate(app, db)
whooshee = Whooshee(app)

from app import routes, models
