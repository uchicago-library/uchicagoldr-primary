from flask import Flask
from flask_wtf import CsrfProtect
import logging
from logging.handlers import RotatingFileHandler

from .views import acquisition
import config

app = Flask(__name__)
CsrfProtect(app)
app.config.from_object(config)
app.register_blueprint(acquisition)
loghandler = RotatingFileHandler('records.log', maxBytes=1024 * 1024 * 100, backupCount=20)
loghandler.setLevel(logging.DEBUG)

logformatter = logging.Formatter("{%(asctime)s -- %(message)s")
loghandler.setFormatter(logformatter)
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(loghandler)

@app.template_filter('strfdate')
def format_date(date, fmt=None):
    format = '%b %d, %Y'
    return date.strftime(format)

@app.template_filter('capfirst')
def capfirst(s):
    return s[0].upper()+s[1:]

@app.template_filter('makePretty')
def makePretty(s):
    if '_' in s:
        parts = s.split('_')
        parts = [x[0].upper()+x[1:].lower() for x in parts]
        return ' '.join(parts)
    else:
        return s[0].upper()+s[1:].lower()