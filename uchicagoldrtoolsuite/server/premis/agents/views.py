from collections import namedtuple
from flask import Blueprint, render_template, Response, request
import json

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
    """returns a JSON output with key 'spooled' and value either 
    True or False
    """
    from .controllers.agentspooler import AgentSpooler
    from .database import db
    print(request.form)
    agentid = request.form.get('agentid')
    eventid = request.form.get('eventid')
    print(eventid)
    print(agentid)
    eventidtype = request.form.get('eventidtype')
    new_link = namedtuple(
                    "newlink", "id eventid, type")(agentid, 
                                                   eventid, 
                                                   eventidtype)
    spooler = AgentSpooler(agentid, 
                           eventid, 
                           eventidtype)
    answer = spooler.spool_data()
    print(answer)
    if answer:
        output = json.dumps({'spooled':'True'})
    else:
        ouput = json.dumps({'spooled':'False'})
    return Response(output, 'text/json')

@agent.route("/newAgent", methods=['POST'])
def addNewAgentRecord():
    """returns a JSON output with key result and value either 
    'SUCCESS or 'FAILURE'
    """
    import json
    agendata = request.form
    creator = AgentCreator(agentdata)
    creation_result = creator.create_agent()
    if creation_result:
        ouput = {'added':'True'}
    else:
        output = {'added':'False'}
    return Response(json.dumps(output), 'text/json')
 
@agent.route("/retrieveAgent", methods=['GET'])
def getAnAgentRecord():
    """returns an XML record describing a particular PREMIS agent
    """
    from tempfile import TemporaryFile
    from .controllers.agentretriever import AgentRetriever
    searchid = request.args.get('agentId', '')
    retriever = AgentRetriever(searchid)
    data = retriever.get_agent_output()
    return Response(data.decode('utf-8'), 'text/xml')
    
@agent.route('/searchAgent', methods=['GET'])
def searchForAnAgent():
    """returns a JSON output with a list of agent identifiers
    """
    from .controllers.agentsearcher import AgentSearcher
    searchword = request.args.get('term', '')
    a = AgentSearcher(searchword)
    a.search()
    output_list = []
    for n in a.result:
        new_dict = {'agent':n}
        output_list.append(new_dict)
    output = {'result':output_list}
    output = json.dumps(output)
    return Response(output, 'text/json')
