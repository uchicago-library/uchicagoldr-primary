from flask import Flask
import logging
from logging.handlers import RotatingFileHandler

from .views import acquisition
import config

app = Flask(__name__)
app.config.from_object(config)
app.register_blueprint(acquisition)
loghandler = RotatingFileHandler('records.log', maxBytes=1024 * 1024 * 100, backupCount=20)
loghandler.setLevel(logging.DEBUG)

logformatter = logging.Formatter("{%(asctime)s -- %(message)s")
loghandler.setFormatter(logformatter)
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(loghandler)

@app.template_filter('strfdate')
def _jinja2_filter_datetime(date, fmt=None):
    format = '%b %d, %Y'
    return date.strftime(format)