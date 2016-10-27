from tempfile import TemporaryDirectory
from uuid import uuid4
from os.path import join
from pathlib import Path
from json import dumps

from pypremis.nodes import *
from pypremis.factories import LinkingEventIdentifierFactory
from pypremis.factories import LinkingObjectIdentifierFactory

from uchicagoldrtoolsuite.core.lib.convenience import iso8601_dt
from ..processors.genericpremiscreator import GenericPREMISCreator
from ..readers.abc.materialsuitepackager import MaterialSuitePackager
from ..ldritems.ldrpath import LDRPath
from ..ldritems.ldritemcopier import LDRItemCopier


class ExternalFileSystemPairTreeMaterialSuitePackager(MaterialSuitePackager):
    def __init__(self, path, root=None):
        self.path = path
        self.root = root
        self.working_dir = TemporaryDirectory()
        self.working_path = join(self.working_dir.name, uuid4().hex)
        self.instantiated_premis = join(self.working_dir.name, uuid4().hex)

    def get_premis(self):
        # Surprise! Nothing coming in externally is assumed to have a valid
        # pre-existing PREMIS record. Instead we are going to whip one into
        # existence and pretend it was there all along. Deleting the packager
        # instance will also delete the temp dir that the premis record
        # is in - so don't do that until you've written it somewhere.
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

            src_item = LDRPath(self.path.decode("utf-8"))
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
            x.item_name = str(Path(self.path.decode('utf-8')).relative_to(self.root))
        else:
            x.item_name = self.path.decode('utf-8')
        return x

    def get_techmd_list(self):
        raise NotImplementedError()

    def get_presform_list(self):
        raise NotImplementedError()
