from .agentproxy import APIAgentProxy

class APIAgentMixin:
    def get_premis_agent_record(self, name=None):
        try:
            name = self.agent_name
        except:
            pass
        if name is None:
            name = str(type(self))
        self._agent_proxy = APIAgentProxy('https://y2.lib.uchicago.edu/ldragents', name=name)
        return self._agent_proxy.record

    def write_premis_agent_record(self):
        self._agent_proxy.sync()
