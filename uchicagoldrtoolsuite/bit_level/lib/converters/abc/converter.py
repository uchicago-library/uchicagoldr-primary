from abc import ABCMeta, abstractmethod

from pypremis.nodes import *

from uchicagoldrtoolsuite.core.lib.convenience import iso8601_dt
from uchicagoldrtoolsuite.core.lib.idbuilder import IDBuilder


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class Converter(metaclass=ABCMeta):

    _claimed_mimes = []

    def __init__(self, input_materialsuite, working_dir, timeout=None):

        self._source_materialsuite = None
        self._working_dir = None
        self._timeout = None
        self._target_extension = None

        self.set_source_materialsuite(input_materialsuite)
        self.set_working_dir(working_dir)
        self.set_timeout(timeout)

    def get_target_extension(self):
        return self._target_extension

    def set_target_extension(self, x):
        if not isinstance(x, str):
            raise TypeError()
        if not x.startswith("."):
            raise ValueError("Extensions must begin with '.'")
        self._target_extension = x

    def get_claimed_mimes(self):
        return self._claimed_mimes

    def get_source_materialsuite(self):
        return self._source_materialsuite

    def get_working_dir(self):
        return self._working_dir

    def get_timeout(self):
        return self._timeout

    def set_source_materialsuite(self, x):
        self._source_materialsuite = x

    def set_working_dir(self, x):
        self._working_dir = x

    def set_timeout(self, x):
        self._timeout = x

    @abstractmethod
    def convert(self):
        pass

    def handle_premis(self, cmd_output, orig_premis, conv_premis, converter_name):
        conv_event = self.build_conv_event(cmd_output, orig_premis, conv_premis, converter_name)
        orig_premis.add_event(
            conv_event
        )
        orig_premis.get_object_list()[0].add_linkingEventIdentifier(
            self._build_linkingEventIdentifier(conv_event)
        )

        if conv_premis:

            # TODO: Decide whether or not to set originalNames for presforms
            # TODONE: I decided not to - because of the weird stuff that would
            # be required with decoding/re-encoding the hex escaped string
            # This will break some old serializers - but shouldn't effect
            # the pairtree serializer in any way

            conv_premis.get_object_list()[0].add_linkingEventIdentifier(
                self._build_linkingEventIdentifier(conv_event)
            )

            crea_event = self.build_crea_event(cmd_output, orig_premis, conv_premis, converter_name)
            conv_premis.add_event(
                crea_event
            )
            conv_premis.get_object_list()[0].add_linkingEventIdentifier(
                self._build_linkingEventIdentifier(crea_event)
            )


            orig_premis.get_object_list()[0].add_relationship(
                self._build_relationship(
                    "derivation",
                    "is Source of",
                    conv_premis.get_object_list()[0],
                    crea_event
                )
            )
            conv_premis.get_object_list()[0].add_relationship(
                self._build_relationship(
                    "derivation",
                    "has Source",
                    orig_premis.get_object_list()[0],
                    crea_event
                )
            )

    def build_conv_event(self, cmd_output, orig_premis, conv_premis, converter_name):
        eventIdentifier = self._build_eventIdentifier()
        eventType = "migration"
        eventDateTime = iso8601_dt()

        conv_event = Event(eventIdentifier, eventType, eventDateTime)

        conv_event.set_eventDetailInformation(
            self._build_eventDetailInformation(
                "Ran a converter ({}) ".format(converter_name) +
                "against the file in an "
                "attempt to create a " +
                "preservation copy."
            )
        )

        conv_event.set_eventOutcomeInformation(
            self._build_eventOutcomeInformation(cmd_output, conv_premis)
        )

        conv_event.set_linkingAgentIdentifier(
            self._build_linkingAgentIdentifier("converter", converter_name)
        )

        conv_event.set_linkingObjectIdentifier(
            self._build_linkingObjectIdentifier(orig_premis, "conversion source")
        )

        if conv_premis:
            conv_event.add_linkingObjectIdentifier(
                self._build_linkingObjectIdentifier(conv_premis, "converted file")
            )

        return conv_event

    def build_crea_event(self, cmd_output, orig_premis, conv_premis, converter_name):
        eventIdentifier = self._build_eventIdentifier()
        eventType = "creation"
        eventDateTime = iso8601_dt()

        crea_event = Event(eventIdentifier, eventType, eventDateTime)

        crea_event.set_eventDetailInformation(
            self._build_eventDetailInformation(
                "Ran a converter ({}) ".format(converter_name) +
                "against the file, creating "
                "this preservation copy "
            )
        )

        crea_event.set_eventOutcomeInformation(
            self._build_eventOutcomeInformation(cmd_output, conv_premis)
        )

        crea_event.add_linkingAgentIdentifier(
            self._build_linkingAgentIdentifier("creator", converter_name)
        )

        crea_event.add_linkingObjectIdentifier(
            self._build_linkingObjectIdentifier(orig_premis, "conversion source")
        )

        crea_event.add_linkingObjectIdentifier(
            self._build_linkingObjectIdentifier(conv_premis, "converted file")
        )

        return crea_event

    def _build_relationship(self, rel_type, rel_subtype, rel_obj, rel_event, seq=None):
        relationshipType = rel_type
        relationshipSubType = rel_subtype
        relatedObjectIdentifier = self._build_relatedObjectIdentifier(rel_obj)
        relationship = Relationship(relationshipType, relationshipSubType, relatedObjectIdentifier)
        relationship.add_relatedEventIdentifier(self._build_relatedEventIdentifier(rel_event))
        return relationship

    def _build_relatedEventIdentifier(self, rel_event, seq=None):
        relatedEventIdentifierType = rel_event.get_eventIdentifier().get_eventIdentifierType()
        relatedEventIdentifierValue = rel_event.get_eventIdentifier().get_eventIdentifierValue()
        relatedEventIdentifier = RelatedEventIdentifier(relatedEventIdentifierType, relatedEventIdentifierValue)
        if seq:
            relatedEventIdentifier.set_relatedEventSequence(seq)
        return relatedEventIdentifier

    def _build_relatedObjectIdentifier(self, obj, seq=None):
        relatedObjectIdentifierType = obj.get_objectIdentifier()[0].get_objectIdentifierType()
        relatedObjectIdentifierValue = obj.get_objectIdentifier()[0].get_objectIdentifierValue()
        relatedObjectIdentifier = RelatedObjectIdentifier(relatedObjectIdentifierType, relatedObjectIdentifierValue)
        if seq:
            relatedObjectIdentifier.set_relatedObjectSequence(seq)
        return relatedObjectIdentifier

    def _build_linkingEventIdentifier(self, event_to_link, seq=None):
        linkingEventIdentifierType = event_to_link.get_eventIdentifier().get_eventIdentifierType()
        linkingEventIdentifierValue = event_to_link.get_eventIdentifier().get_eventIdentifierValue()
        linkingEventIdentifier = LinkingEventIdentifier(linkingEventIdentifierType,
                                                        linkingEventIdentifierValue)
        if seq:
            linkingEventIdentifier.set_relatedEventSequence(seq)
        return linkingEventIdentifier

    def _build_eventIdentifier(self):
        id_tup = IDBuilder().build('premisID').show()
        eventIdentifierType = id_tup[0]
        eventIdentifierValue = id_tup[1]
        return EventIdentifier(eventIdentifierType, eventIdentifierValue)

    def _build_eventDetailInformation(self, eventDetailInfoStr):
        eventDetail = eventDetailInfoStr
        eventDetailInformation = EventDetailInformation(
            eventDetail=eventDetail
        )
        return eventDetailInformation

    def _build_eventOutcomeInformation(self, cmd_output, conv_premis):
        if conv_premis is not None:
            eventOutcome = "SUCCESS"
        else:
            eventOutcome = "FAIL"
        eventOutcomeDetail = self._build_eventOutcomeDetail(cmd_output)
        eventOutcomeInformation = EventOutcomeInformation(
            eventOutcome=eventOutcome,
            eventOutcomeDetail=eventOutcomeDetail
        )
        return eventOutcomeInformation

    def _build_eventOutcomeDetail(self, cmd_output):
        eventOutcomeDetailNote = str(cmd_output[1])
        eventOutcomeDetail = EventOutcomeDetail(
            eventOutcomeDetailNote=eventOutcomeDetailNote
        )
        return eventOutcomeDetail

    def _build_linkingAgentIdentifier(self, agentRole, agent_name):
        agentID = self.look_up_agent(agent_name)
        if agentID is None:
            id_tup = IDBuilder().build('premisID').show()
            linkingAgentIdentifierType = id_tup[0]
            linkingAgentIdentifierValue = id_tup[1]
            agentID = LinkingAgentIdentifier(linkingAgentIdentifierType,
                                             linkingAgentIdentifierValue)
        agentID.set_linkingAgentRole(agentRole)
        return agentID

    def _build_linkingObjectIdentifier(self, premis_to_link, linkRole):
        linkingObjectIdentifierType = premis_to_link.get_object_list()[0].get_objectIdentifier()[0].get_objectIdentifierType()
        linkingObjectIdentifierValue = premis_to_link.get_object_list()[0].get_objectIdentifier()[0].get_objectIdentifierValue()
        x = LinkingObjectIdentifier(linkingObjectIdentifierType, linkingObjectIdentifierValue)
        x.set_linkingObjectRole(linkRole)
        return x

    def look_up_agent(self, x):
        return None

    claimed_mimes = property(get_claimed_mimes)
    source_materialsuite = property(get_source_materialsuite, set_source_materialsuite)
    working_dir = property(get_working_dir, set_working_dir)
    timeout = property(get_timeout, set_timeout)
    target_extension = property(get_target_extension, set_target_extension)
