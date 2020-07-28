from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config['JSON_AS_ASCII'] = False

from app import routes
