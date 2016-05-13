from tempfile import TemporaryDirectory
from uuid import uuid1
from os.path import join

from pypremis.lib import PremisRecord
from pypremis.nodes import *

from .ldrpath import LDRPath
from .ldritemoperations import copy
from .abc.ldritem import LDRItem
from ...core.lib.bash_cmd import BashCommand
from ...core.lib.convenience import iso8601_dt


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class GenericTechnicalMetadataCreator(object):
    """
    Ingests a stage structure and produces a FITS xml record for every
    file in it.
    """
    def __init__(self, stage):
        """
        spawn a technical metadata creator that should work regardless of
        what kind of LDRItems are being used

        __Args__

        stage (Stage): the Stage to operate on
        """
        self.stage = stage
        # This instance var should hold the dir open until the instance is
        # deleted from whatever script spawned it. Aka move this stuff
        # somewhere before your instance gets garbage collected.
        self.working_dir = TemporaryDirectory()
        self.working_dir_path = self.working_dir.name

    def process(self, skip_existing=False):
        for segment in self.stage.segment_list:
            for materialsuite in segment.materialsuite_list:
                if not isinstance(materialsuite.get_premis(), LDRItem):
                    raise ValueError("All material suites must have a PREMIS " +
                                     "record in order to generated technical " +
                                     "metadata records.")
                if skip_existing:
                    if isinstance(materialsuite.get_technicalmetadata(0), LDRItem):
                        continue
                techmd, premis = self.instantiate_and_make_techmd(materialsuite)
                materialsuite.set_technicalmetadata_list(techmd)
                materialsuite.set_premis(premis)
                if materialsuite.presform_list is not None:
                    for presform_ms in materialsuite.presform_list:
                        pres_techmd, pres_premis = \
                            self.instantiate_and_make_techmd(presform_ms)
                        presform_ms.set_technicalmetadata_list(pres_techmd)
                        presform_ms.set_premis(pres_premis)

    def instantiate_and_make_techmd(self, ms):
        """
        write the file to disk an examine it, update its PREMIS

        __Args__

        1. ms (MaterialSuite): The MaterialSuite of the item in question

        __Returns__

        * (tuple): The first entry is a list of one element, the technical
            metadata.
            The second is the updated record PREMIS record.
        """
        recv_file = join(self.working_dir_path, str(uuid1()))
        recv_item = LDRPath(recv_file)
        fits_file = join(self.working_dir_path, str(uuid1()))
        copy(ms.content, recv_item, clobber=True)

        com = BashCommand(['fits', '-i', recv_file, '-o', fits_file])
        com.set_timeout(43200)
        com.run_command()

        premis_path = join(self.working_dir_path, str(uuid1()))
        premis_item = LDRPath(premis_path)
        copy(ms.premis, premis_item, True)

        premis = PremisRecord(frompath=premis_path)
        premis.add_event(self._build_event(premis, com.get_data()))
        updated_premis_path = join(self.working_dir_path, str(uuid1()))
        premis.write_to_file(updated_premis_path)

        return ([LDRPath(fits_file)], LDRPath(updated_premis_path))

    def _build_event(self, premis, com_data):
        """
        build an event entry for this FITS run

        __Returns__

        * event (pypremis.nodes.Event): The event node
        """
        eventIdentifier = self._build_eventIdentifier()
        eventType = "description"
        eventDateTime = iso8601_dt()
        event = Event(eventIdentifier, eventType, eventDateTime)
        event.set_eventDetailInformation(
            self._build_eventDetailInformation()
        )
        event.set_eventOutcomeInformation(
            self._build_eventOutcomeInformation(com_data)
        )
        event.set_linkingAgentIdentifier(
            self._build_linkingAgentIdentifier()
        )
        event.set_linkingObjectIdentifier(
            self._build_linkingObjectIdentifier(premis)
        )
        return event

    def _build_eventIdentifier(self):
        """
        build an eventIdentifier node for this FITS run

        __Returns__

        * eventIdentifier(pypremis.nodes.EventIdentifier): the event id node
        """
        eventIdentifierType = "DOI"
        eventIdentifierValue = str(uuid1())
        eventIdentifier = EventIdentifier(eventIdentifierType,
                                          eventIdentifierValue)
        return eventIdentifier

    def _build_eventDetailInformation(self):
        """
        build an eventDetailInformation node for this FITS run

        __Returns__

        * eventDetailInformation (pypremis.nodes.EventDetailInformation):
            the built eventDetailInformation node
        """
        eventDetail = "ran File Information Tool Set (FITS available at " + \
            "http://projects.iq.harvard.edu/fits/home) over file"
        eventDetailInformation = EventDetailInformation(
            eventDetail=eventDetail)
        return eventDetailInformation

    def _build_eventOutcomeInformation(self, com_data):
        """
        build an eventOutcomeInformation node for this FITS run

        __Returns__

        * eventOutcomeInformation (pypremis.nodes.EventOutcomeInformation):
            the built node
        """
        if com_data[2] is True:
            eventOutcome = "SUCCESS"
        else:
            eventOutcome = "FAIL"
        eventOutcomeDetail = self._build_eventOutcomeDetail(com_data)
        eventOutcomeInformation = EventOutcomeInformation(
            eventOutcome=eventOutcome,
            eventOutcomeDetail=eventOutcomeDetail
        )
        return eventOutcomeInformation

    def _build_eventOutcomeDetail(self, com_data):
        """
        build and eventOutcomeDetail node for this FITS run

        __Returns__

        * eventOutcomeDetail (pypremis.nodes.EventOutcomeDetail):
            the built node
        """
        eventOutcomeDetailNote = str(com_data[1])
        eventOutcomeDetail = EventOutcomeDetail(
            eventOutcomeDetailNote=eventOutcomeDetailNote
        )
        return eventOutcomeDetail

    def _build_linkingAgentIdentifier(self):
        """
        build a linkingAgentIdentifier node for this FITS run

        __Returns__

        * linkingAgentIdentifier (pypremis.nodes.LinkingAgentIdentifier):
            the built node
        """
        linkingAgentIdentifier = self.look_for_own_agent_id_in_db()
        if linkingAgentIdentifier is None:
            linkingAgentIdentifierValue = str(uuid1())
            linkingAgentIdentifierType = "DOI"
            linkingAgentIdentifier = LinkingAgentIdentifier(
                linkingAgentIdentifierType, linkingAgentIdentifierValue
            )
            linkingAgentIdentifier.set_linkingAgentRole('software describer')
        return linkingAgentIdentifier

    def _build_linkingObjectIdentifier(self, premis):
        """
        build a linkingObjectIdentifier node for this FITS run

        __Returns__

        * linkingObjectIdentifier (pypremis.nodes.LinkingObjectIdentifier):
            the built node
        """
        linkingObjectRole = "Described object"
        # These lines are obnoxious
        linkingObjectIdentifierType = premis.get_object_list()[0].\
            get_objectIdentifier()[0].get_objectIdentifierType()
        linkingObjectIdentifierValue = premis.get_object_list()[0].\
            get_objectIdentifier()[0].get_objectIdentifierValue()
        linkingObjectIdentifier = LinkingObjectIdentifier(
            linkingObjectIdentifierType, linkingObjectIdentifierValue
        )
        linkingObjectIdentifier.set_linkingObjectRole(linkingObjectRole)
        return linkingObjectIdentifier

    def look_for_own_agent_id_in_db(self):
        """
        go look in the PREMIS db to see if this agent already has an id
        """
        # to be implemented in the future
        return None
