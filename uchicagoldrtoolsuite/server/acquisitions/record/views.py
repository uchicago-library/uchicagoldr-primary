
from flask import Blueprint

blueprint = Blueprint('records', __name__, 
                      template_folder='templates')

@blueprint.route('/')
def frontpage():
    return str("hello, this is the front page of " + 
            "the acquisitions record application")