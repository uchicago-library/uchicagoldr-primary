from tempfile import TemporaryDirectory
from uuid import uuid4
from os import fsencode, fsdecode
from os.path import join
from pathlib import Path
from json import dumps

from pypremis.nodes import *
from pypremis.factories import LinkingEventIdentifierFactory
from pypremis.factories import LinkingObjectIdentifierFactory

from uchicagoldrtoolsuite.core.lib.convenience import iso8601_dt
from uchicagoldrtoolsuite.core.lib.convenience import bytes_to_hex_str
from ..processors.genericpremiscreator import GenericPREMISCreator
from ..readers.abc.materialsuitepackager import MaterialSuitePackager
from ..ldritems.ldrpath import LDRPath
from ..ldritems.ldritemcopier import LDRItemCopier

# The handling of paths in this class is an interesting conundrum - because the
# different major OSes use different canonical path representations (bytes on
# Unixs {and OSX I think} and unicode {utf-16?} in Windows-land) but
# pathlib.Path only accepts string arguments this might be tricky to get working
# flawlessly cross platform.
# Right now I think I am going to go with trying to coerce representations,
# regardless of how they come in, into strings.

class ExternalFileSystemMaterialSuitePackager(MaterialSuitePackager):
    """
    Point at a file - get a MaterialSuite
    It's like magic!
    (Not really, it packages the filepath as an LDRPath and dynamically
    creates a stub PREMIS record for the file with some precomputed info,
    so really nothing like magic).
    """
    def __init__(self, path, root=None):
        self._str_path = None
        self._bytes_path = None
        self._str_root = None
        self._bytes_root = None
        super().__init__()
        self.path = path
        if self.root is not None:
            self.root = root
        self.working_dir = TemporaryDirectory()
        self.working_path = join(self.working_dir.name, uuid4().hex)
        self.instantiated_premis = join(self.working_dir.name, uuid4().hex)

    def package(self):
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
                    eventOutcomeInformation=build_eventOutcomeInformation(copyreport)
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

        def write_minimal_premis(minimal_premis_record):
            minimal_premis_record.write_to_file(self.instantiated_premis)

        ingestion_event = copy_to_working()
        minimal_premis_record = generate_minimal_premis(ingestion_event)
        link_em_all_up(minimal_premis_record)
        write_minimal_premis(minimal_premis_record)
        return LDRPath(self.instantiated_premis)

    def get_content(self):
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

    def get_bytes_path(self):
        return self._bytes_path

    def get_str_path(self):
        return self._str_path

    def set_path(self, x):
        self._str_path = fsdecode(x)
        self._bytes_paths = fsencode(x)

    def get_bytes_root(self):
        return self._bytes_root

    def get_str_root(self):
        return self._str_root

    def set_root(self, x):
        self._str_root = fsdecode(x)
        self._bytes_root = fsencode(x)

    path = property(get_str_path, set_path)
    bpath = property(get_bytes_path, set_path)
    root = property(get_str_root, set_root)
    broot = property(get_bytes_root, set_root)
