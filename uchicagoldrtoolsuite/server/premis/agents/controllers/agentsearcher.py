
import re

from ..models.PremisAgent import PremisAgent

class AgentSearcher(object):
    def __init__(self, term):
        self.query_term = term
        self.search()
        
    def get_query_term(self):
        return self._query_term
    
    def set_query_term(self, value):
        if re.compile('\w{1,}').match(value):
            self._query_term = value
        else:
            raise ValueError("query term can only be one word long")
    
    def search(self):
        from ..database import db
        result = db.session.query(PremisAgent).filter(PremisAgent.name.contains(self.query_term))
        if result.count() > 0:
            self.result = [x.identifier for x in result]
        else:
            self.result = []
            
    query_term = property(get_query_term, set_query_term)