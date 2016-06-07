
from flask import Blueprint, render_template

from .controllers.agentcreator import AgentCreator
from .controllers.agentsearcher import AgentSearcher
from .controllers.agentspool import AgentSpool

__author__ = "Tyler Danstrom"
__email__ = "tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


blueprint = Blueprint('agents', __name__, 
                      template_folder='templates')

@blueprint.route("/linkAgent", methods=['POST'])
def linkEventToAgent():
    agentid = request.args.get('agentid', '')
    eventid = request.args.get('eventid', '')
    eventidtype = request.args.get('eventidtype', '')
    new_link = namedtuple("newlink", "id type")(agentid, agentype)
    spooler = AgentSpooler().append(agentid, new_link)
    return spooler.status

@blueprint.route("/newAgent", methods=['POST'])
def addNewAgentRecord():
    agendata = request.form
    creator = AgentCreator(agentdata)
    return agentcreator.status

@blueprint.route("/retrieveAgent", methods=['GET'])
def getAnAgentRecord(agentid):
    searchid = request.args.get('agentid', '')
    retriever = AgentRetriever(searchid)
    return render_template('fullagent.json', result=a.data, 
                           errors=a.errors)

@blueprint.route('/searchAgent', methods=['GET'])
def searchForAnAgent(term):
    searchword = request.args.get('term', '')
    a = AgentSearcher(term)
    return render_template_template('searchresult.json', 
                                    result=a.data,
                                    errors=a.errors)
