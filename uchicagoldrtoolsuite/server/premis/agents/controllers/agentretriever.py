
class AgentRetriever(object):
    def __init__(self, term_id):
        self.agent_id = term_id
        
    def get_agent_id(self):
        return self._agent_id
    
    def set_agent_id(self, value):
        from ..models.PremisAgent import db, PremisAgent
        print(db)
        if isinstance(value, str):
            print(db)
            print(value)
            result = db.session.query(PremisAgent).filter(PremisAgent.identifier==value)
            print([x for x in result])
            self._agent_id = value
            
    def show_agent(self):
        return "hi there"
    
    agent_id = property(get_agent_id, set_agent_id)