import requests

from pypremis.nodes import Agent, AgentIdentifier, LinkingEventIdentifier

from .abc.agentdatabase import AgentDatabase


class APIAgentDatabase(AgentDatabase):
    def __init__(self, api_root):
        self.api_root = api_root

    @staticmethod
    def _okay_json(resp_json):
        if not (resp_json['errors'] == None and
                resp_json['status'] == 'success'):
            raise ValueError(
                "API Error! Status: {}, Errors: {}".format(
                    resp_json['status'], str(resp_json['errors'])
                )
            )

    def mint_agent(self, agentName, agentType="software"):
        data = {
            'fields': ['name', 'type'],
            'name': agentName,
            'type': agentType
        }
        r = requests.post(self.api_root + "/agents", json=data)
        r.raise_for_status()
        j = r.json()
        self._okay_json(j)
        identifier = j['data']['agents']['identifier']
        return identifier

    def search_agents(self, query):
        r = requests.get(self.api_root + "/agents")
        r.raise_for_status()
        j = r.json()
        self._okay_json(j)
        result = {j['data']['agents'][x]['identifier'] for x in
                  j['data']['agents'] if
                  j['data']['agents'][x]['name'] == query}
        return result

    def add_linkingEventIdentifier(self, agentIdentifier, eventIdentifier):
        r = requests.post(
              self.api_root + "/agents/" + agentIdentifier + "/events",
              json={'event': eventIdentifier}
        )
        r.raise_for_status()
        self._okay_json(r.json())

    def agent_exists(self, agentIdentifier):
        r = requests.head(self.api_root + "/agents/" + agentIdentifier)
        if r.status_code < 399:
            return True
        else:
            return False

    def get_record(self, agentIdentifier):
        r = requests.get(self.api_root + "/agents/" + agentIdentifier)
        r.raise_for_status()
        j = r.json()
        self._okay_json(j)
        agent_json = j['data']['agent']
        agentIdentifier = AgentIdentifier('uuid', agent_json['identifier'])
        agent = Agent(agentIdentifier)
        if agent_json.get('name', False):
            agent.set_agentName(agent_json['name'])
        if agent_json.get('type', False):
            agent.set_agentType(agent_json['type'])
        if agent_json.get('events', False):
            for x in set(agent_json['events']):
                agent.add_linkingEventIdentifier(
                    LinkingEventIdentifier('uuid', x)
                )
        return agent
