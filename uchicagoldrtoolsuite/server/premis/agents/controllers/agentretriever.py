
from pypremis.nodes import Agent, AgentIdentifier

class AgentRetriever(object):
    def __init__(self, term_id):
        self.agent_id = term_id
        
    def get_agent_id(self):
        return self._agent_id
    
    def set_agent_id(self, value):
        from ..models.PremisAgent import db, PremisAgent
        matching_agent = db.session.query(PremisAgent).filter(PremisAgent.identifier==self.agent_id)
        if matching_agent.count() < 1 or matching_agent.count() > 1:
            return False
        else:
            result = None
            for n_agent in matching_agent:
                result = n_agent
            id_element = AgentIdentifier('DOI', n_agent.identifier)
            agent_premis = Agent(id_element)
            agent_premis.add_agentName(n_agent.name)
            self.agent_id = value
            self_agent_record = agent_premis.toXML()
            return agent_premis.toXML()
            
    def show_agent(self):
        return "hi there"
    
    agent_id = property(get_agent_id, set_agent_id)