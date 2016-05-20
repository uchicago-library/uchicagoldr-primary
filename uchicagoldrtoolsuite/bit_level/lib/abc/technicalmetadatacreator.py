from os.path import join
from abc import ABCMeta, abstractmethod
from uuid import uuid1

from pypremis.lib import PremisRecord
from pypremis.nodes import *

from ..ldrpath import LDRPath
from ....core.lib.convenience import iso8601_dt
from ..ldritemoperations import copy


class TechnicalMetadataCreator(metaclass=ABCMeta):

    _source_materialsuite = None
    _working_dir = None
    _timeout = None

    @abstractmethod
    def __init__(self, materialsuite, working_dir, timeout=None):
        self.set_source_materialsuite(materialsuite)
        self.set_working_dir(working_dir)
        self.set_timeout(timeout)

    def get_source_materialsuite(self):
        return self._source_materialsuite

    def set_source_materialsuite(self, x):
        self._source_materialsuite = x

    def get_working_dir(self):
        return self._working_dir

    def set_working_dir(self, x):
        self._working_dir = x

    def get_timeout(self):
        return self._timeout

    def set_timeout(self, x):
        self._timeout = x

    @abstractmethod
    def process(self):
        pass

    def handle_premis(self, cmd_output, material_suite, techmdcreator_name,
                      success):
        premis_path = join(self.working_dir, str(uuid1()))
        copy(material_suite.get_premis(), LDRPath(premis_path))
        orig_premis = PremisRecord(frompath=premis_path)
        event = self._build_Event(cmd_output, techmdcreator_name, success,
                                  orig_premis.get_object_list()[0])
        orig_premis.add_event(event)

        orig_premis.get_object_list()[0].add_linkingEventIdentifier(
            self._build_linkingEventIdentifier(event)
        )

        updated_premis_path = join(self.working_dir, str(uuid1()))
        orig_premis.write_to_file(updated_premis_path)

        material_suite.set_premis(
            LDRPath(updated_premis_path)
        )

    def _build_Event(self, cmd_output, techmdcreator_name, success, link_obj):
        eventIdentifier = self._build_eventIdentifier()
        eventType = "description"
        eventDateTime = iso8601_dt()

        event = Event(eventIdentifier, eventType, eventDateTime)

        event.add_eventDetailInformation(
            self._build_eventDetailInformation(techmdcreator_name)
        )
        event.add_eventOutcomeInformation(
            self._build_eventOutcomeInformation(cmd_output, success)
        )
        event.add_linkingAgentIdentifier(
            self._build_linkingAgentIdentifier(techmdcreator_name, 'describer')
        )
        event.add_linkingObjectIdentifier(
            self._build_linkingObjectIdentifier(link_obj, 'analysis source')
        )
        return event

    def _build_eventIdentifier(self):
        eventIdentifierType = "DOI"
        eventIdentifierValue = str(uuid1())
        return EventIdentifier(eventIdentifierType, eventIdentifierValue)

    def _build_eventDetailInformation(self, techmdcreator_name):
        eventDetail = "Ran {} on the ".format(techmdcreator_name) + \
            "content in order to generate technical metadata."
        return EventDetailInformation(eventDetail=eventDetail)

    def _build_eventOutcomeInformation(self, cmd_output, success):
        if success:
            eventOutcome = "SUCCESS"
        else:
            eventOutcome = "FAIL"

        eventOutcomeDetail = EventOutcomeDetail(
            eventOutcomeDetailNote=str(cmd_output)
        )
        return EventOutcomeInformation(
            eventOutcome=eventOutcome,
            eventOutcomeDetail=eventOutcomeDetail
        )

    def _build_linkingAgentIdentifier(self, techmdcreator_name, role):
        agent_id = self.look_up_agent(techmdcreator_name)
        if agent_id is None:
            linkingAgentIdentifierType = "DOI"
            linkingAgentIdentifierValue = str(uuid1())
            agent_id = LinkingAgentIdentifier(linkingAgentIdentifierType,
                                              linkingAgentIdentifierValue)
        agent_id.set_linkingAgentRole(role)
        return agent_id

    def _build_linkingObjectIdentifier(self, obj, role):
        linkingObjectIdentifierType = \
            obj.get_objectIdentifier()[0].get_objectIdentifierType()
        linkingObjectIdentifierValue = \
            obj.get_objectIdentifier()[0].get_objectIdentifierValue()
        obj_id = LinkingObjectIdentifier(linkingObjectIdentifierType,
                                         linkingObjectIdentifierValue)
        obj_id.set_linkingObjectRole(role)
        return obj_id

    def _build_linkingEventIdentifier(self, event):
        linkingEventIdentifierType = \
            event.get_eventIdentifier().get_eventIdentifierType()
        linkingEventIdentifierValue = \
            event.get_eventIdentifier().get_eventIdentifierValue()
        return LinkingEventIdentifier(linkingEventIdentifierType,
                                      linkingEventIdentifierValue)

    def look_up_agent(self, x):
        return None

    source_materialsuite = property(
        get_source_materialsuite,
        set_source_materialsuite
    )

    working_dir = property(
        get_working_dir,
        set_working_dir
    )

    timeout = property(
        get_timeout,
        set_timeout
    )
