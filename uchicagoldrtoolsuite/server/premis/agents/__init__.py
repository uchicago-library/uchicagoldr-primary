
from flask import Flask

from .views import agent
import config

app = Flask(__name__)
app.config.from_object(config)
app.register_blueprint(agent)
