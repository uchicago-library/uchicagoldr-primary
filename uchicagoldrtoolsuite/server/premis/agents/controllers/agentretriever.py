
from tempfile import TemporaryFile

from pypremis.lib import PremisRecord
from pypremis.nodes import Agent, AgentIdentifier

class AgentRetriever(object):
    def __init__(self, term_id):
        self.agent_id = term_id
        self.generate_record()
    
    def generate_record(self):
        from ..models.PremisAgent import db, PremisAgent
        search = db.session.query(PremisAgent).filter(PremisAgent.identifier==self.agent_id)
        agent_record = search[0]
        id_element = AgentIdentifier('DOI', agent_record.identifier)
        agent_premis = Agent(id_element)
        agent_premis.add_agentName(agent_record.name)
        self.agent_record = PremisRecord(agents=[agent_premis])
    
    def get_agent_output(self):
        return self.agent_record.get_agent_list()[0].toXML()
        
    def get_agent_id(self):
        return self._agent_id
    
    def set_agent_id(self, value):
        from ..models.PremisAgent import db, PremisAgent
        matching_agent = db.session.query(PremisAgent).filter(PremisAgent.identifier==value)
        if matching_agent.count() < 1 or matching_agent.count() > 1:
            raise ValueError("invalid agent identifier")
        else:
            self._agent_id = value
        
    def get_agent_record(self):
        return self._agent_record
    
    def set_agent_record(self, value):
        if isinstance(value, PremisRecord):
            self._agent_record = value
        else:
            raise ValueError("agent_record has to be a PremisRecord")
            
    agent_id = property(get_agent_id, set_agent_id)
    agent_record = property(get_agent_record, set_agent_record)