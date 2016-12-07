from logging import getLogger
from tempfile import TemporaryDirectory
from uuid import uuid4
from os import fsencode, fsdecode
from os.path import join
from pathlib import Path
from json import dumps

from pypremis.nodes import *
from pypremis.factories import LinkingEventIdentifierFactory
from pypremis.factories import LinkingObjectIdentifierFactory

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.convenience import iso8601_dt
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, \
    log_init_success
from ..processors.genericpremiscreator import GenericPREMISCreator
from ..readers.abc.materialsuiteserializationreader import \
    MaterialSuiteSerializationReader
from ..ldritems.ldrpath import LDRPath
from ..ldritems.ldritemcopier import LDRItemCopier


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


# The handling of paths in this class is an interesting conundrum - because the
# different major OSes use different canonical path representations (bytes on
# Unixs {and OSX I think} and unicode {utf-16?} in Windows-land) but
# pathlib.Path only accepts string arguments this might be tricky to get working
# flawlessly cross platform.
# Right now I think I am going to go with trying to coerce representations,
# regardless of how they come in, into strings.


class ExternalFileSystemMaterialSuiteReader(MaterialSuiteSerializationReader):
    """
    Point at a file - get a MaterialSuite
    It's like magic!
    (Not really, it packages the filepath as an LDRPath and dynamically
    creates a stub PREMIS record for the file with some precomputed info,
    so really nothing like magic).
    """
    @log_aware(log)
    def __init__(self, path, root=None, run_name=None):
        """
        Instantiate a new packager

        __Args__

        1. path (str/bytes): The fullpath to the target file

        __KWArgs__

        * root (str/bytes): A subpath of the fullpath. The canonical name of
            the file then becomes its path relative to this root.
        """
        log_init_attempt(self, log, locals())
        self._str_path = None
        self._bytes_path = None
        self._str_root = None
        self._bytes_root = None
        super().__init__(root, uuid4().hex)
        self.path = path
        self.working_dir = TemporaryDirectory()
        self.working_path = join(self.working_dir.name, uuid4().hex)
        self.instantiated_premis = join(self.working_dir.name, uuid4().hex)
        self.run_name = run_name
        log_init_success(self, log)

    @log_aware(log)
    def package(self):
        """
        The interface method for packagers

        __Returns__

        * (MaterialSuite): The external file packaged as a MaterialSuite
        """
        # Because the PREMIS file is this weird made up thing in a TempDir
        # we have to keep the temporary directory around for the duration
        # of the life of the structure - otherwise it poofs out of existence
        # with the packager and we've just packaged a bunch of stuff that
        # doesn't exist anymore. My (temporary?) solution to this is to cram
        # a reference to the temporary directory into the resulting structure
        # itself, which isn't particular pretty, but I think it will work
        # as expected in nearly all the obvious cases.
        self.struct._tmpdir = self.working_dir
        return super().package()

    @log_aware(log)
    def get_premis(self):
        # Surprise! Nothing coming in externally is assumed to have a valid
        # pre-existing PREMIS record. Instead we are going to whip one into
        # existence and pretend it was there all along.
        def copy_to_working():

            def build_ingestion_event(copyreport):

                def build_eventIdentifier():
                    return EventIdentifier("uuid", uuid4().hex)

                def build_eventOutcomeInformation(copyreport):
                    if copyreport['src_eqs_dst']:
                        outcome = "success"
                    else:
                        outcome = "failure"
                    note = dumps(copyreport)
                    eventOutcomeDetail = EventOutcomeDetail(
                        eventOutcomeDetailNote=note
                    )
                    return EventOutcomeInformation(
                        eventOutcome=outcome,
                        eventOutcomeDetail=eventOutcomeDetail
                    )

                e = Event(
                    build_eventIdentifier(), "ingestion",
                    iso8601_dt(),
                    eventOutcomeInformation=build_eventOutcomeInformation(
                        copyreport
                    )
                )
                return e

            src_item = LDRPath(self.path)
            dst_item = LDRPath(self.working_path)
            copier = LDRItemCopier(src_item, dst_item)
            cr = copier.copy()
            event = build_ingestion_event(cr)
            return event

        def generate_minimal_premis(ingestion_event):
            if self.root:
                original_name = str(Path(self.path).relative_to(self.root))
            else:
                original_name = self.path
            record = GenericPREMISCreator.make_record(
                self.working_path, original_name
            )
            record.add_event(ingestion_event)
            return record

        def link_em_all_up(record):
            obj = record.get_object_list()[0]
            event = record.get_event_list()[0]

            obj.add_linkingEventIdentifier(
                LinkingEventIdentifierFactory(event).produce_linking_node()
            )
            event.add_linkingObjectIdentifier(
                LinkingObjectIdentifierFactory(obj).produce_linking_node()
            )

        def add_eventDetailInformation(event):
            if not self.run_name:
                eventDetail = "Run Identifier (Machine Generated): {}".format(
                    str(uuid4().hex)
                )
            else:
                eventDetail = "Run Identifier (Human Generated): {}".format(
                    str(self.run_name)
                )
            eventDetailInformation = EventDetailInformation(
                eventDetail=eventDetail
            )
            event.add_eventDetailInformation(eventDetailInformation)

        def write_minimal_premis(minimal_premis_record):
            minimal_premis_record.write_to_file(self.instantiated_premis)

        log.info("Copying external file to tmp location")
        ingestion_event = copy_to_working()
        add_eventDetailInformation(ingestion_event)
        log.info("Creating ingest PREMIS")
        minimal_premis_record = generate_minimal_premis(ingestion_event)
        link_em_all_up(minimal_premis_record)
        log.info("Writing ingest PREMIS")
        write_minimal_premis(minimal_premis_record)
        return LDRPath(self.instantiated_premis)

    @log_aware(log)
    def get_content(self):
        log.info("Packaging original file as an LDRPath")
        x = LDRPath(self.working_path)
        if self.root is not None:
            x.item_name = str(Path(self.path).relative_to(self.root))
        else:
            x.item_name = self.path
        return x

    def get_techmd_list(self):
        raise NotImplementedError()

    def get_presform_list(self):
        raise NotImplementedError()

    @log_aware(log)
    def get_bytes_path(self):
        return self._bytes_path

    @log_aware(log)
    def get_str_path(self):
        return self._str_path

    @log_aware(log)
    def set_path(self, x):
        log.debug("Attempting to set path as both str and bytes...")
        self._str_path = fsdecode(x)
        self._bytes_paths = fsencode(x)

    @log_aware(log)
    def get_bytes_root(self):
        return self._bytes_root

    @log_aware(log)
    def get_str_root(self):
        return self._str_root

    @log_aware(log)
    def set_root(self, x):
        self._str_root = fsdecode(x)
        self._bytes_root = fsencode(x)

    # Byte equivalent properties are prefaced with a b
    path = property(get_str_path, set_path)
    bpath = property(get_bytes_path, set_path)
    root = property(get_str_root, set_root)
    broot = property(get_bytes_root, set_root)
