
from datetime import datetime

from pypremis.nodes import Event, EventIdentifier, EventOutcomeInformation,\
    LinkingAgentIdentifier, LinkingObjectIdentifier

from uchicagoldrtoolsuite.core.lib.idbuilder import IDBuilder

from .ldritemoperations import get_an_agent_id


class ArchivePremisEvent(object):
    def __init__(self, objid_nodes):
        self.linkable_objects = objid_nodes
        self.linkable_agent_type,\
            self.linkable_agent_value = get_an_agent_id('archiver')
        self.identifier = IDBuilder().build('eventID')

    def build_event(self):
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
        return self._linkable_objects

    def set_linkable_objects(self, value):
        if not getattr(self, '_linkable_objects', None):
            self._linkable_objects = value

    def get_linkable_agent(self):
        return self._linkable_agent

    def set_linkable_agent(self, value):
        if not getattr(self, '_linkable_agent', None):
            self._linkable_agent = value

    def get_identifier(self):
        return self._identifier

    def set_identifier(self, value):
        if not getattr(self, '_identifier', None):
            self._identifier = value

    linkable_agents = property(
        get_linkable_agent, set_linkable_agent)
    linkable_objects = property(
        get_linkable_objects, set_linkable_objects)
    identifier = property(get_identifier, set_identifier)
