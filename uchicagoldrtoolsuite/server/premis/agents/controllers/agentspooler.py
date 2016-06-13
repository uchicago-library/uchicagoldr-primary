
from os.path import abspath, exists, join
from pathlib import Path

from uchicagoldrtoolsuite.core.lib.idbuilder import IDBuilder

from .datasourceselector import DataSourceSelector
from pypremis.nodes import AgentIdentifier

__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class AgentSpooler(object):
    def __init__(self, agentid, eventid, eventidtype):
        self.agentid = agentid
        self.eventid = eventid
        self.eventidtype = eventidtype
        self.status = 0
        
    def spool_data(self):
        from ..models.Spool import db, Spool
        new_spool_item = Spool()
        new_spool_item.agentID = self.agentid 
        new_spool_item.eventID = self.eventid 
        new_spool_item.eventIDType = self.eventidtype
        try:
            db.session.add(new_spool_item)
            db.session.commit()
            return  True
        except:
            return False
    
    def get_agentid(self):
        return self._agentid
    
    def set_agentid(self, value):
        if isinstance(value, str) and len(value) == 32:
            self._agentid = value
        else:
            raise ValueError("invalid agentid in agentspooler")
        
    def get_eventid(self):
        return self._eventid
    
    def set_eventid(self, value):
        print(value)
        print(len(value))
        if isinstance(value, str) and len(value) == 32:
            self._eventid = value
        else:
            raise ValueError("invalid eventid in agentspooler")
    
    def get_eventidtype(self):
        return self._eventidtype
    
    def set_eventidtype(self, value):
        if value.lower() == 'doi':
            self._eventidtype = value
        else:
            raise ValueError("event id type can only be DOI")
    
    agentid = property(get_agentid, set_agentid)
    eventid = property(get_eventid, set_eventid)
    eventidtype = property(get_eventidtype, set_eventidtype)
    