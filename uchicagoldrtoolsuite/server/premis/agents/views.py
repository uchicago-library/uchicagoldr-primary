
from flask import Blueprint

blueprint = Blueprint('agents', __name__, 
                      template_folder='templates')

@blueprint.route("/", methods=['GET'])
def frontpage():
    return "hi this is a front page of the agents service"

@blueprint.route("/linkAgent", methods=['POST'])
def linkEventToAgent():
    return "linking event endpoint"

@blueprint.route("/newAgent", methods=['POST'])
def addNewAgentRecord():
    return "new agent endpoint"

@blueprint.route("/retrieveAgent", methods=['GET'])
def getAnAgentRecord():
    return "get a specific agent endpoint"

@blueprint.route('/searchAgent', methods=['GET'])
def searchForAnAgent():
    return "searching for an agent endpoint"