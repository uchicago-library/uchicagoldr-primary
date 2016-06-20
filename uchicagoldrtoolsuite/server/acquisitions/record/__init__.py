
from flask import Flask
from .views import acquisition

app = Flask(__name__)
app.register_blueprint(acquisition)
