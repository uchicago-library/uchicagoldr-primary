
class AgentCreator(object):
    def __init__(self, data_dict):
        self.role = data_dict.ge('agentrole', '')
        self.type = data_dict.get('agenttype', '')
        self.name = data_dict.get('agentname', '')
    
    def save_data(self):
        from .models.PremisAgent import db, PremisAgent
        new_agent = PremisAgent()
        new_id_type, new_id = IDBuilder().build('agentID').show()
        new_agent.role = self.role
        new_agent.agentType = self.type
        new_agent.name = self.name
        new_agent.identifier = new_id
        try:
            db.session.add(new_agent)
            db.session.commit()
            return True
        except:
            return False
        