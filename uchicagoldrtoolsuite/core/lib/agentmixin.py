from .abc.agentdatabase import AgentDatabase

class AgentMixin:

    _agent_db = None
    _agent_name = None

    def get_agent_db(self):
        return self._agent_db

    def set_agent_db(self, x):
        if not isinstance(x, AgentDatabase) or x is None:
            raise TypeError()
        self._agent_db = x

    def get_agent_name(self):
        return self._agent_name

    def set_agent_name(self, x):
        if x is None:
            self._agent_name = None
        self._agent_name = str(x)

    agent_database = property(get_agent_db, set_agent_db)
    agent_name = property(get_agent_name, set_agent_name)
