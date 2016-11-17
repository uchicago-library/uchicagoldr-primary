from abc import ABCMeta, abstractmethod
from pathlib import Path
from uuid import uuid4
import mimetypes
from os.path import splitext, isfile
from logging import getLogger

from pypremis.nodes import *
from pypremis.lib import PremisRecord

from uchicagoldrtoolsuite.core.lib.convenience import iso8601_dt
from uchicagoldrtoolsuite.core.lib.idbuilder import IDBuilder
from uchicagoldrtoolsuite.bit_level.lib.ldritems.ldrpath import LDRPath
from uchicagoldrtoolsuite.bit_level.lib.structures.materialsuite import MaterialSuite
from uchicagoldrtoolsuite.bit_level.lib.ldritems.ldritemcopier import LDRItemCopier
from uchicagoldrtoolsuite.bit_level.lib.processors.genericpremiscreator import GenericPREMISCreator


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class Converter(metaclass=ABCMeta):
    """
    Defines and partially implements a workflow for archive-safe file conversion

    The Converter ABC should be used as the base class for all converters
    which operate on MaterialSuites. Converters claim mime-types which they
    can handle the conversions for (claimed extensions do this by proxy) and
    emit a new MaterialSuite which contains a preservation stable copy of a file
    with an attached PREMIS record. These PREMIS records should accurately
    reflect the relation of the relation of the new stable file to the file
    from which it was derived.

    In the event of failure the Converter should update the PREMIS metadata
    of the original file, such that the attempt at conversion (despite it
    failing) is recorded.
    """

    # Mime names abiding by https://tools.ietf.org/html/rfc4288#section-4.2 in
    # theory, and matching the output of magic.from_file() or
    # mimetypes.guess_type() in practice.
    _claimed_mimes = []

    # Extension, including a preceeding dot. Anything that can be mapped by
    # mimetypes.types_map to a mime will be added to the _claimed_mimes array
    # when a child class calls super().__init__()
    _claimed_extensions = []

    # Flipped to true when an instance claims its mimes from provided extensions
    _claimed_list_initd = False

    def __init__(self, input_materialsuite, working_dir, timeout=None):
        """
        Superclass init for converters. Handles setting instance variables
        and some basic setup.

        __Args__

        * input_materialsuite (MaterialSuite): The MaterialSuite containing the
            original file and the associated PREMIS record
        * working_dir (pathlike): A temporary directory where the converter
            can dump intermediate files, as well as the final product

        __KWArgs__

        1) timeout (int): Time (in seconds) to block for a conversion process.
            After {timeout} seconds have gone by SIGTERM is sent to the external
            process.
        """
        self._source_materialsuite = None
        self._working_dir = None
        self._timeout = None
        self._converter_name = "Converter ABC"

        self.claim_mimes_from_extensions()
        self.set_source_materialsuite(input_materialsuite)
        self.set_working_dir(working_dir)
        self.set_timeout(timeout)

    @classmethod
    def claim_mimes_from_extensions(cls):
        """
        Iterate through the claimed extensions, trying to map them into mimes
        to be read out of the original's PREMIS
        """
        # This might be faster if I made _claimed_mimes a set - but with
        # datasets of this size I suspect it wouldn't buy anymore than a few
        # micro(nano?) seconds speedup, and would make the class syntax weirder
        if not cls._claimed_list_initd:
            mimetypes.init()
            for x in cls._claimed_extensions:
                x = mimetypes.types_map.get(x, None)
                if x is not None and x not in cls._claimed_mimes:
                    cls._claimed_mimes.append(x)
        cls._claimed_list_initd = True

    @classmethod
    def handles_mime(cls, mime):
        """
        Alerts external code as to whether or not the converter handles {mime}

        __Args__

        mime (str): A mimetype

        __Returns__

        (bool): True if the mime is handled, false otherwise
        """
        cls.claim_mimes_from_extensions()
        if mime in cls._claimed_mimes:
            return True
        return False

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

    def get_converter_name(self):
        return self._converter_name

    def set_converter_name(self, x):
        self._converter_name = x

    def instantiate_original(self, premis=None):
        """
        Writes the bytestream from the original MaterialSuite to disk
        Attempts to give the file an accurate extension to help some external
        converter processes which rely on file extensions by looking at either
        the originalName field (if it has an extension) or by trying to
        extrapolate the extension from the mimetype.

        __KWArgs__

        * premis (PremisRecord): The PREMIS which defines the original file

        __Returns__

        * target_path (str): The path the instantiated original byte data is
            now at.
        """
        target_path = str(Path(self.working_dir, uuid4().hex))
        # if we have the PREMIS try to set an extension, just in case the
        # converter requires it
        if premis is not None:
            path_altered = False
            try:
                ext = splitext(premis.get_object_list()[0].get_originalName())[1]
                if ext is not '':
                    target_path = target_path + ext
                    path_altered = True
            except:
                pass
            if not path_altered:
                try:
                    ext = mimetypes.guess_extension(premis.get_object_list()[0].get_objectCharacteristics()[0].get_format()[0].get_formatName())
                    target_path = target_path + ext
                except:
                    pass

        target_ldritem = LDRPath(target_path)
        c = LDRItemCopier(self.source_materialsuite.content, target_ldritem)
        r = c.copy()
        if r['src_eqs_dst'] is not True:
            raise RuntimeError("Bad Copy!")
        return target_path

    def instantiate_and_read_original_premis(self):
        """
        Dumps the byte data out of an LDRItem and reads it as PREMIS

        __Returns__

        (PremisRecord): A PREMIS metadata record object.
        """
        target_path = Path(self.working_dir, uuid4().hex)
        target_ldritem = LDRPath(str(target_path))
        c = LDRItemCopier(self.source_materialsuite.premis, target_ldritem)
        r = c.copy()
        if r['src_eqs_dst'] is not True:
            raise RuntimeError("Bad Copy!")
        return PremisRecord(frompath=str(target_path))

    @abstractmethod
    def run_converter(self, in_path):
        """
        The abstract method which runs the specific converter in each subclass.

        __Args__

        1. in_path (str): A filesystem path to the file to be converted

        __Returns__

        Each subclass must return a dictionary from this method with two keys:
            1. outpath
            2. cmd_output

        The value attached to the outpath key must be either a string or None
        (and it should be None if the conversion fails).

        The value of cmd_output.__str__() is written into the PREMIS record
        as part of the event metadata.
        """
        pass

    def generate_presform_premis_record(self, presform_path):
        """
        Wraps the creation of a stub PREMIS record, so its name is more explicit

        __Args__

        1. presform_path (str): A file system path with a newly created
            preservation stable file

        __Returns__

        (PremisRecord): A stub PREMIS record describing the file at
            {presform_path}
        """
        return GenericPREMISCreator.make_record(presform_path)

    def handle_premis(self, cmd_output, orig_premis, conv_premis, converter_name):
        """
        Handles creating conversion events and linking records
        In the event of a failed conversion handles the creation of a failure
        event in the original PREMIS record.

        __Args__

        1. cmd_output (CompletedProcess/*): Data inserted as event information
            into the event entity.

        2. orig_premis (PremisRecord): The PREMIS metadata for the original
            object

        3. conv_premis (PremisRecord || None): The PREMIS metadata for the
            converted object, or None if conversion failed

        4. converter_name (str): What this converter calls itself for record
            keeping purposes.
        """
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
        """
        TODO: Looks up an agent from a centralized source
        """
        # TODO
        return None

    def convert(self):
        """
        The general interface for all converter classes.

        Defines a conversion workflow which makes no assumptions about the
        input bytestreams

        __Returns__

        * f (MaterialSuite) || (None): The resulting MaterialSuite, or None
            in the event of a failed conversion
        """
        orig_premis = self.instantiate_and_read_original_premis()
        target = self.instantiate_original(premis=orig_premis)
        results = self.run_converter(target)
        outpath = results.get('outpath', None)
        if outpath is not None:
            presform_premis = self.generate_presform_premis_record(outpath)
        else:
            presform_premis = None
        self.handle_premis(results['cmd_output'], orig_premis, presform_premis, self.converter_name)
        updated_premis_fp = Path(self.working_dir, uuid4().hex)
        orig_premis.write_to_file(str(updated_premis_fp))
        self.source_materialsuite.premis = LDRPath(str(updated_premis_fp))
        if outpath is not None:
            presform_premis_fp = str(Path(self.working_dir, uuid4().hex))
            presform_premis.write_to_file(presform_premis_fp)
            f = MaterialSuite()
            f.identifier = presform_premis.get_object_list()[0].get_objectIdentifier()[0].get_objectIdentifierValue()
            f.content = LDRPath(outpath)
            f.premis = LDRPath(presform_premis_fp)
            return f

    claimed_mimes = property(get_claimed_mimes)
    source_materialsuite = property(get_source_materialsuite, set_source_materialsuite)
    working_dir = property(get_working_dir, set_working_dir)
    timeout = property(get_timeout, set_timeout)
    converter_name = property(get_converter_name, set_converter_name)
