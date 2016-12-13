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
    """
    minimally functional, can only update linkingEventIdentifiers
    """
    gr = requests.get(
            api_root + "/agents/" +
            record.get_agentIdentifier()[0].get_agentIdentifierValue() +
            "/events"
    )
    okay_response(gr)
    okay_json(gr.json())
    existing_events = gr.json()['data']['agent events']['events']
    existing_events = set(existing_events)
    try:
        events = set([x.get_linkingEventIdentifierValue() for x in
                      record.get_linkingEventIdentifier()])
    except KeyError:
        events = set()
    diff_events = events - existing_events
    for x in diff_events:
        r = requests.post(
            api_root + "/agents/" +
            record.get_agentIdentifier()[0].get_agentIdentifierValue() +
            "/events",
            json={'event': x}
        )
        okay_response(r)
        okay_json(r.json())
