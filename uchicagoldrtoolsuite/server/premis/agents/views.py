
from flask import Blueprint

blueprint = Blueprint('agents', __name__, 
                      template_folder='templates')

@blueprint.route("/", methods=['GET'])
def frontpage():
    return "hi this is a front page of the agents service"