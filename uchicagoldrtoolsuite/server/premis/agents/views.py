
from flask import Blueprint, render_template

from .controllers.agentsearcher import AgentSearcher, RetrieveAgent

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
    agendata = request.form
    agentcreator = CreateNewAgent(agentdata)
    return render_template('updateinfo.json', result=agentcreator.status)

@blueprint.route("/retrieveAgent", methods=['GET'])
def getAnAgentRecord(agentid):
    searchid = request.args.get('agentid', '')
    if searchid:
        a = RetrieveAgent(searchid)
    else:
        result = None
    return render_template('fullagent.json', result=result)

@blueprint.route('/searchAgent?', methods=['GET'])
def searchForAnAgent(term):
    searchword = request.args.get('term', '')
    if searchword:
        a = AgentSearcher(term)
    else:
        result = None
    return render_template_template('searchresult.json', result=result)