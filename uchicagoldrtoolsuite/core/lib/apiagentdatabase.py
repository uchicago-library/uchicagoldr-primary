import requests
from collections import OrderedDict

from pypremis.nodes import Agent, AgentIdentifier, LinkingEventIdentifier

from .abc.agentdatabase import AgentDatabase


class APIAgentDatabase(AgentDatabase):

    CACHE_SIZE=500000

    def __init__(self, api_root):
        self._cached_searches = OrderedDict()
        self._cached_agents = OrderedDict()
        self.api_root = api_root

    @staticmethod
    def _okay_response(resp):
        if resp.status_code != 200:
            raise ValueError(
                "Bad HTTP Status Code (not 200), return code: {}".format(
                    str(resp.status_code)
                )
            )

    @staticmethod
    def _okay_json(resp_json):
        if not (resp_json['errors'] == None and
                resp_json['status'] == 'success'):
            raise ValueError(
                "API Error! Status: {}, Errors: {}".format(
                    resp_json['status'], str(resp_json['errors'])
                )
            )

    def dump_search_cache(self):
        self._cached_searches = OrderedDict()

    def dump_agent_cache(self):
        self._cached_agents = OrderedDict()

    def dump_caches(self):
        self.dump_search_cache()
        self.dump_agent_cache()

    def mint_agent(self, agentName, agentType="software"):
        data = {
            'fields': ['name', 'type'],
            'name': agentName,
            'type': agentType
        }
        r = requests.post(self.api_root + "/agents", json=data)
        self._okay_response(r)
        j = r.json()
        self._okay_json(j)
        identifier = j['data']['agents']['identifier']
        if agentName in self._cached_searches:
            self._cached_searches[agentName].append(identifier)
        return identifier

    def search_agents(self, query, use_cache=True):
        if query in self._cached_searches and use_cache:
            return self._cached_searches[query]
        r = requests.get(self.api_root + "/agents")
        self._okay_response(r)
        j = r.json()
        self._okay_json(j)
        result = {j['data']['agents'][x]['identifier'] for x in
                  j['data']['agents'] if
                  j['data']['agents'][x]['name'] == query}
        self._cached_searches[query] = result
        if len(self._cached_searches) > self.CACHE_SIZE:
            self._cached_searches.popitem(last=False)
        return result

    def add_linkingEventIdentifier(self, agentIdentifier, eventIdentifier):
        r = requests.post(
              self.api_root + "/agents/" + agentIdentifier + "/events",
              json={'event': eventIdentifier}
        )
        self._okay_response(r)
        self._okay_json(r.json())
        if agentIdentifier in self._cached_agents:
            self._cached_agents[agentIdentifier].add_linkingEventIdentifier(
                'uuid', eventIdentifier
            )

    def agent_exists(self, agentIdentifier):
        r = requests.head(self.api_root + "/agents/" + agentIdentifier)
        if r.status_code < 399:
            return True
        else:
            return False

    def get_record(self, agentIdentifier, use_cache=True):
        if agentIdentifier in self._cached_agents and use_cache:
            return self._cached_agents[agentIdentifier]
        r = requests.get(self.api_root + "/agents/" + agentIdentifier)
        self._okay_response(r)
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
        self._cached_agents[agentIdentifier] = agent
        if len(self._cached_agents) > self.CACHE_SIZE:
            self._cached_agents.popitem(last=False)
        return agent
