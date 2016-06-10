from collections import namedtuple
from flask import Blueprint, render_template, request

__author__ = "Tyler Danstrom"
__email__ = "tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"

agent = Blueprint('agents', __name__, 
                      template_folder='templates')

@agent.route("/linkAgent", methods=['POST', 'GET'])
def linkEventToAgent():
    from .controllers.agentspooler import AgentSpooler
    from .database import db
    print(request.form)
    agentid = request.form.get('agentid')
    eventid = request.form.get('eventid')
    eventidtype = request.form.get('eventidtype')
    new_link = namedtuple("newlink", "id eventid, type")(agentid, 
                                                         eventid, 
                                                         eventidtype)
    spooler = AgentSpooler(agentid, 
                           eventid, 
                           eventidtype)
    new_item = spooler.spool_data()
    db.session.add(new_item)
    db.session.commit()
    return "success"

@blueprint.route("/newAgent", methods=['POST'])
def addNewAgentRecord():
    agendata = request.form
    creator = AgentCreator(agentdata)
    creation_result = creator.create_agent()
    if creation_result:
        return "success"
    else:
        return "failed"
 
@agent.route("/retrieveAgent", methods=['GET'])
def getAnAgentRecord():
    from .controllers.agentretriever import AgentRetriever
    searchid = request.args.get('agentid', '')
    retriever = AgentRetriever(searchid)
    return retriever.show_agent()
 
@agent.route('/searchAgent', methods=['GET'])
def searchForAnAgent():
    from .controllers.agentsearcher import AgentSearcher
    searchword = request.args.get('term', '')
    print(searchword)
    a = AgentSearcher(searchword)
    a.search()
    return str(a.result)
