from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET
from pathlib import Path
from os.path import join
from uuid import uuid1
from .bash_cmd import BashCommand
from pypremis.lib import PremisRecord
from pypremis.nodes import *
from .convenience import iso8601_dt


class TechnicalMetadataRecordCreator(object):
    def __init__(self, path, premis_record, timeout=None):
        self.cmd_out = None
        self.record = None
        self.premis_record = premis_record
        self.file_path = Path(path)
        self.timeout = timeout
        if not self.file_path.is_file():
            raise ValueError("The technical metadata creator requires " +
                             "an existing filepath as input.")
        with TemporaryDirectory() as tmpdir:
            self.fits_path = self.make_fits_in_tmp(self.file_path, tmpdir,
                                                   timeout=self.timeout)
            self.record = self.read_fits(self.fits_path)
        self.premis_record = self.update_premis(self.premis_record)

    def make_record(self, file_path, timeout=None):
        return make_fits_in_tmp

    def make_fits_in_tmp(self, file_path, tmpdir, timeout=None):
            outfilename = str(uuid1())
            outpath = join(tmpdir, outfilename)
            cmd = BashCommand(['fits', '-i',
                               getattr(self.file_path, 'path', str(self.file_path)),
                               '-o', outpath])
            if timeout:
                cmd.set_timeout(timeout)
            cmd.run_command()
            self.cmd_out = cmd.get_data()
            return outpath

    def read_fits(self, fits_path):
        tree = ET.parse(fits_path)
        return tree

    def get_record(self):
        return self.record

    def get_premis(self):
        return self.premis_record

    def update_premis(self, premis_record):
        self.premis_record.add_event(self._build_event())
        return self.premis_record

    def _build_event(self):
        eventIdentifier = self._build_eventIdentifier()
        eventType = "description"
        eventDateTime = iso8601_dt()
        event = Event(eventIdentifier, eventType, eventDateTime)
        event.set_eventDetailInformation(self._build_eventDetailInformation())
        event.set_eventOutcomeInformation(self._build_eventOutcomeInformation())
        event.set_linkingAgentIdentifier(self._build_linkingAgentIdentifier())
        event.set_linkingObjectIdentifier(self._build_linkingObjectIdentifier())
        return event

    def _build_eventIdentifier(self):
        eventIdentifierType = "DOI"
        eventIdentifierValue = str(uuid1())
        eventIdentifier = EventIdentifier(eventIdentifierType,
                                          eventIdentifierValue)
        return eventIdentifier

    def _build_eventDetailInformation(self):
        eventDetail = "ran File Information Tool Set (FITS available at " + \
        "http://projects.iq.harvard.edu/fits/home) over file"
        eventDetailInformation = EventDetailInformation(
            eventDetail=eventDetail)
        return eventDetailInformation

    def _build_eventOutcomeInformation(self):
        if self.cmd_out[2] is True:
            eventOutcome = "SUCCESS"
        else:
            eventOutcome = "FAIL"
        eventOutcomeDetail = self._build_eventOutcomeDetail()
        eventOutcomeInformation = EventOutcomeInformation(
            eventOutcome=eventOutcome,
            eventOutcomeDetail=eventOutcomeDetail
        )
        return eventOutcomeInformation

    def _build_eventOutcomeDetail(self):
        eventOutcomeDetailNote = str(self.cmd_out[1])
        return eventOutcomeDetailNote

    def _build_linkingAgentIdentifier(self):
        linkingAgentIdentifier = self.look_for_own_agent_id_in_db()
        if linkingAgentIdentifier is None:
            linkingAgentIdentifierValue = str(uuid1())
            linkingAgentIdentifierType = "DOI"
            linkingAgentIdentifier = LinkingAgentIdentifier(
                linkingAgentIdentifierType, linkingAgentIdentifierValue
            )
            linkingAgentIdentifier.set_linkingAgentRole('software describer')
        return linkingAgentIdentifier

    def _build_linkingObjectIdentifier(self):
        linkingObjectRole = "Described object"
        linkingObjectIdentifierType = self.premis_record.get_object_list()[0].get_objectIdentifier()[0].get_objectIdentifierType()
        linkingObjectIdentifierValue = self.premis_record.get_object_list()[0].get_objectIdentifier()[0].get_objectIdentifierValue()
        linkingObjectIdentifier = LinkingObjectIdentifier(
            linkingObjectIdentifierType, linkingObjectIdentifierValue
        )
        linkingObjectIdentifier.set_linkingObjectRole(linkingObjectRole)
        return linkingObjectIdentifier

    def look_for_own_agent_id_in_db(self):
        return None
