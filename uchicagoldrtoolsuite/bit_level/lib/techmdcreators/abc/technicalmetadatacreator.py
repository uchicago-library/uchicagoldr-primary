from os.path import join
from logging import getLogger
from abc import ABCMeta, abstractmethod
from uuid import uuid1

from pypremis.lib import PremisRecord
from pypremis.nodes import *

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.convenience import iso8601_dt
from uchicagoldrtoolsuite.core.lib.idbuilder import IDBuilder
from ...ldritems.ldrpath import LDRPath
from ...ldritems.ldritemcopier import LDRItemCopier


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class TechnicalMetadataCreator(metaclass=ABCMeta):
    """
    The abstract base class for TechnicalMetadataCreators
    specifies the .process() interface method, as well as provided
    a helper init to be called in subclasses and the logic for handling
    PREMIS updates given the results operations in the .process() method.
    """

    _source_materialsuite = None
    _working_dir = None
    _timeout = None

    @abstractmethod
    @log_aware(log)
    def __init__(self, materialsuite, working_dir, timeout=None):
        """
        A helper init to ease handling of init vars in child classes.

        __Args__

        1. materialsuite (MaterialSuite): The MaterialSuite to create
            technical metadata for
        2. working_dir (str): A directory in which the converter class
            can write files
        3. timeout (int): A timeout for the technical metadata creation
            process, after which the techmd creator will fail out.
        """
        log.debug("Entering the ABC init")
        self.set_source_materialsuite(materialsuite)
        self.set_working_dir(working_dir)
        self.set_timeout(timeout)
        log.debug("Exiting the ABC init")

    @log_aware(log)
    def get_source_materialsuite(self):
        return self._source_materialsuite

    @log_aware(log)
    def set_source_materialsuite(self, x):
        self._source_materialsuite = x

    @log_aware(log)
    def get_working_dir(self):
        return self._working_dir

    @log_aware(log)
    def set_working_dir(self, x):
        self._working_dir = x

    @log_aware(log)
    def get_timeout(self):
        return self._timeout

    @log_aware(log)
    def set_timeout(self, x):
        self._timeout = x

    @abstractmethod
    @log_aware(log)
    def process(self):
        pass

    @log_aware(log)
    def handle_premis(self, cmd_output, material_suite, techmdcreator_name,
                      success):
        """
        Handles altering the MaterialSuites PREMIS after processing.
        Either records successful techmd creation, or failure.

        This function should be called *within* a child classes .process()

        __Args__

        1. cmd_output (.__repr__()-able): Gets written into the
            eventOutcomeDetailNote
        2. material_suite (MaterialSuite): The MaterialSuite which was acted on
        3. techmdcreator_name (str): What the techmd creator should be referred
            to as in the PREMIS record
        4. success (bool): If true records the event outcome as successful,
            otherwise records the event outcome as a failure.
        """
        premis_path = join(self.working_dir, str(uuid1()))
        LDRItemCopier(material_suite.get_premis(), LDRPath(premis_path)).copy()
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

    @log_aware(log)
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

    @log_aware(log)
    def _build_eventIdentifier(self):
        id_tup = IDBuilder().build('premisID').show()
        eventIdentifierType = id_tup[0]
        eventIdentifierValue = id_tup[1]
        return EventIdentifier(eventIdentifierType, eventIdentifierValue)

    @log_aware(log)
    def _build_eventDetailInformation(self, techmdcreator_name):
        eventDetail = "Ran {} on the ".format(techmdcreator_name) + \
            "content in order to generate technical metadata."
        return EventDetailInformation(eventDetail=eventDetail)

    @log_aware(log)
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

    @log_aware(log)
    def _build_linkingAgentIdentifier(self, techmdcreator_name, role):
        agent_id = self.look_up_agent(techmdcreator_name)
        if agent_id is None:
            id_tup = IDBuilder().build('premisID').show()
            linkingAgentIdentifierType = id_tup[0]
            linkingAgentIdentifierValue = id_tup[1]
            agent_id = LinkingAgentIdentifier(linkingAgentIdentifierType,
                                              linkingAgentIdentifierValue)
        agent_id.set_linkingAgentRole(role)
        return agent_id

    @log_aware(log)
    def _build_linkingObjectIdentifier(self, obj, role):
        linkingObjectIdentifierType = \
            obj.get_objectIdentifier()[0].get_objectIdentifierType()
        linkingObjectIdentifierValue = \
            obj.get_objectIdentifier()[0].get_objectIdentifierValue()
        obj_id = LinkingObjectIdentifier(linkingObjectIdentifierType,
                                         linkingObjectIdentifierValue)
        obj_id.set_linkingObjectRole(role)
        return obj_id

    @log_aware(log)
    def _build_linkingEventIdentifier(self, event):
        linkingEventIdentifierType = \
            event.get_eventIdentifier().get_eventIdentifierType()
        linkingEventIdentifierValue = \
            event.get_eventIdentifier().get_eventIdentifierValue()
        return LinkingEventIdentifier(linkingEventIdentifierType,
                                      linkingEventIdentifierValue)

    @log_aware(log)
    def look_up_agent(self, x):
        # TODO
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
