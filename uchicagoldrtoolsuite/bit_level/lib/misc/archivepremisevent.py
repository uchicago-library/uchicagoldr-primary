
from datetime import datetime

from pypremis.nodes import Event, EventIdentifier, EventOutcomeInformation,\
    LinkingAgentIdentifier, LinkingObjectIdentifier

from uchicagoldrtoolsuite.core.lib.idbuilder import IDBuilder

from .ldritemoperations import get_an_agent_id

__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class ArchivePremisEvent(object):
    """ArchivePremisEvent is meant to be used to to create a premis record
    event describing an object's ingestion into the archive space
    """
    def __init__(self, objid_nodes):
        """initializes an ArchivePremisEvent object
        
        __Args__
        1. objid_nodes (list): a list of strings that are purported to be
        object identifiers
        """
        self.linkable_objects = objid_nodes
        self.linkable_agent_type = 'DOI'
        self.linkable_agent_value = get_an_agent_id('archiver')
        self.identifier = IDBuilder().build('eventID')

    def build_event(self):
        """returns a pypremis Event node that contains a valid premis event element 
        describing ingestion to the archive space
        """
        event_id_type, event_id_value = self.identifier.show()
        event_id_node = EventIdentifier(event_id_type, event_id_value)
        new_event_node = Event(
            event_id_node, 'ingestion', datetime.now().isoformat())
        event_outcomeinfo_node = EventOutcomeInformation(
            eventOutcome='SUCCESS')
        new_event_node.set_eventOutcomeInformation(event_outcomeinfo_node)
        linking_agent = LinkingAgentIdentifier(
                self.linkable_agent_type, self.linkable_agent_value)
        new_event_node.set_linkingAgentIdentifier(linking_agent)
        for obj in self.linkable_objects:
            event_object_id = LinkingObjectIdentifier(obj[0], obj[1])
            new_event_node.add_linkingObjectIdentifier(event_object_id)
        return new_event_node

    def get_linkable_objects(self):
        """returns the linkable_objects data attribute value
        """
        return self._linkable_objects

    def set_linkable_objects(self, value):
        """sets the linkable_objects data attribute value
        """
        if not getattr(self, '_linkable_objects', None):
            self._linkable_objects = value

    def get_linkable_agent(self):
        """returns the linkable_agent data attribute
        """
        return self._linkable_agent

    def set_linkable_agent(self, value):
        """sets the linkable_data attribute value
        """
        if not getattr(self, '_linkable_agent', None):
            self._linkable_agent = value

    def get_identifier(self):
        """returns the identifier data attribute value 
        """
        return self._identifier

    def set_identifier(self, value):
        """sets the identifier data attribute value
        """
        if not getattr(self, '_identifier', None):
            self._identifier = value

    linkable_agents = property(
        get_linkable_agent, set_linkable_agent)
    linkable_objects = property(
        get_linkable_objects, set_linkable_objects)
    identifier = property(get_identifier, set_identifier)
