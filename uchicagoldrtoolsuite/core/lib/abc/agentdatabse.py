from abc import ABCMeta, abstractmethod

class AgentDatabase(metaclass=ABCMeta):
    @abstractmethod
    def mint_agent(self, agentName, agentType=None):
        pass

    @abstractmethod
    def search_agents(self, query):
        pass

    @abstractmethod
    def add_linkingEventIdentifier(self, id, lei):
        pass
