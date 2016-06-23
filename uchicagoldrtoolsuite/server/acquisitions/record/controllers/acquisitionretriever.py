
from ..models.Acquisition import db, Acquisition

class AcquisitionRetriever(object):
    def __init__(self):
        self.session = db.session
        self.queryable = Acquisition
        self.result = None
        
    def run_browse(self):
        search = db.session.query(Acquisition)
        
        self.result = sorted([(x.id, x.createdDate, x.isAccessioned) for x in search], key=lambda x: x[2])
        
    def get_session(self):
        return self._session
    
    def set_session(self, value):
        self._session = value
        
    def get_queryable(self):
        return self._queryable
    
    def set_queryable(self, value):
        if getattr(self, 'queryable', None):
            pass
        else:
            self._queryable = Acquisition
    
    def get_result(self):
        return self._result
    
    def set_result(self, value):
        if not getattr(self, 'result', None) and isinstance(value, list):
            self._result = value

    session = property(get_session, set_session)
    queryable = property(get_queryable, set_queryable)
    result = property(get_result, set_result)