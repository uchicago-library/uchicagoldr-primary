from uuid import uuid4

import requests

from pypremis.nodes import Agent, AgentIdentifier, LinkingEventIdentifier


def okay_response(resp):
    if resp.status_code != 200:
        raise ValueError(
            "Bad HTTP Status Code (not 200), return code: {}".format(
                str(resp.status_code)
            )
        )


def okay_json(resp_json):
    if not (resp_json['errors'] == None and resp_json['status'] == 'success'):
        raise ValueError(
            "API Error! Status: {}, Errors: {}".format(
                resp_json['status'], str(resp_json['errors'])
            )
        )


def agent_from_json(agent_json):
    agentIdentifier = AgentIdentifier("uuid", agent_json['identifier'])
    linkingEventIdentifiers = []
    for x in agent_json['events']:
        linkingEventIdentifiers.append(
            LinkingEventIdentifier("uuid", x)
        )
    agent = Agent(agentIdentifier)
    agent.set_agentName(agent_json['name'])
    agent.set_agentType(agent_json['type'])
    for x in linkingEventIdentifiers:
        agent.add_linkingEventIdentifier(x)
    return agent


def get_json(endpoint):
    resp = requests.get(endpoint)
    okay_response(resp)
    resp_json = resp.json()
    okay_json(resp_json)
    return resp_json


def api_retrieve_agent(api_root, identifier):
    resp_json = get_json(api_root + "/agents/" + identifier)
    agent_json = resp_json['data']['agent']
    agent = agent_from_json(agent_json)
    return agent


def api_search_agent(api_root, name):
    resp_json = get_json(api_root + "/agents")
    agents = resp_json['data']['agents']
    matching_agents = [agents[x] for x in agents if agents[x]['name'] == name]
    return [agent_from_json(x) for x in matching_agents]


def mint_agent(identifier=None, name=None):
    if identifier is None:
        identifier = uuid4().hex
    agentIdentifier = AgentIdentifier("uuid", identifier)
    agent = Agent(agentIdentifier)
    if name is not None:
        agent.add_agentName(str(name))
    return agent


def api_update_agent(api_root, record):
    data = {}
    data['type'] = record.get_agentType(),
    data['identifier'] = record.get_agentIdentifier()[0].get_agentIdentifierValue(),
    if record.get_agentName()[0]:
        data['name'] = record.get_agentName()[0],
    try:
        data['events'] = [x.get_linkingEventIdentifierValue() for x in
                          record.get_linkingEventIdentifier()]
    except KeyError:
        pass
    data['fields'] = [x for x in data.keys()]
    r = requests.post(
        api_root + "/agents/" +
        record.get_agentIdentifier()[0].get_agentIdentifierValue(),
        data=data
    )
    okay_response(r)
