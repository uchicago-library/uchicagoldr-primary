from os.path import join, isdir, isfile, splitext
from json import load

from pypremis.lib import PremisRecord

from pypairtree.pairtree import PairTree
from pypairtree.utils import identifier_to_path

from .abc.archiveserializationreader import ArchiveSerializationReader
from ..structures.segment import Segment
from ..structures.materialsuite import MaterialSuite
from ..structures.presformmaterialsuite import PresformMaterialSuite
from ..ldritems.ldrpath import LDRPath


class FileSystemArchiveReader(ArchiveSerializationReader):
    def __init__(self):
        super().__init__()

    def _read_skeleton(self, lts_path, identifier):
        arch_root = join(lts_path, str(identifier_to_path(identifier)), "arf")
        pairtree_root = join(arch_root, "pairtree_root")
        admin_root = join(arch_root, "admin")
        if not isdir(arch_root):
            raise ValueError("No such identifier ({}) in the long term " +
                             "storage environment ({})!".format(
                                 lts_path, identifier))
        if not isdir(pairtree_root):
            raise ValueError("No pairtree root in Archive ({})!".format(
                identifier))
        if not isdir(admin_root):
            raise ValueError("No admin directory in Archive ({})!".format(
                identifier))

        admin_manifest_path = join(admin_root, "admin_manifest.json")
        data_manifest_path = join(admin_root, "data_manifest.json")
        accrec_dir_path = join(admin_root, "accession_records")
        adminnotes_path = join(admin_root, "adminnotes")
        legalnotes_path = join(admin_root, "legalnotes")

        if not isfile(admin_manifest_path):
            raise ValueError("No admin_manifest.json in Archive ({})!".format(
                identifier))
        if not isfile(data_manifest_path):
            raise ValueError("No data_manifest.json in Archive ({})!".format(
                identifier))
        if not isdir(accrec_dir_path):
            raise ValueError()
        if not isdir(adminnotes_path):
            raise ValueError()
        if not isdir(legalnotes_path):
            raise ValueError()

        return arch_root, pairtree_root, admin_root, admin_manifest_path, \
            data_manifest_path, accrec_dir_path, adminnotes_path, \
            legalnotes_path

    def read(self, lts_path, identifier):
        self.get_struct().identifier = identifier
        arch_root, pairtree_root, admin_root, admin_manifest_path, \
            data_manifest_path, accrec_dir_path, adminnotes_path, \
            legalnotes_path = self._read_skeleton(lts_path, identifier)

        pairtree = PairTree(containing_dir=arch_root)
        pairtree.gather_objects()

        data_manifest = None
        with open(data_manifest_path, 'r') as f:
            data_manifest = load(f)

        if not data_manifest['acc_id'] == identifier:
            raise ValueError("Identifier mismatch with data_manifest.json")

        ids_from_manifest = [x['identifier'] for x in data_manifest['objs']]
        num_ids_from_manifest = len(ids_from_manifest)
        i = 0
        for obj in pairtree.objects:
            if obj.identifier not in ids_from_manifest:
                raise ValueError("ID on filesystem that isn't in the " +
                                 "manifest: {}".format(obj.identifier))
            i += 1
        if i != num_ids_from_manifest:
            raise ValueError("ID(s) in the manifest that aren't on the " +
                             "file system!")

        for ms_entry in data_manifest['objs']:
            # Create a segment if one doesn't exist with that identifier
            # otherwise grab the existing segment from the structure
            is_presform = False
            seg = None
            for x in self.get_struct().segment_list:
                if x.identifier == ms_entry['origin_segment']:
                    seg = x
            if seg is None:
                seg = Segment(
                    ms_entry['origin_segment'].split("-")[0],
                    int(ms_entry['origin_segment'].split("-")[1])
                )
                self.get_struct().add_segment(seg)
            premis_path = None
            for bytestream_entry in ms_entry['bytestreams']:
                if bytestream_entry['type'] == "PREMIS":
                    premis_path = bytestream_entry['dst']
                    premis = PremisRecord(frompath=premis_path)
                    try:
                        relationships = premis.get_object_list()[0].get_relationship()
                    except KeyError:
                        relationships = []
                    for x in relationships:
                        if x.get_relationshipType() == "derivation" and \
                                x.get_relationshipSubType() == "has Source":
                            is_presform = True
            if not is_presform:
                seg.add_materialsuite(
                    self._pack_materialsuite(ms_entry,
                                            data_manifest)
                )

        return self.get_struct()

    def _pack_materialsuite(self, ms_entry, data_manifest):
        ms = MaterialSuite()
        premis = None
        for bytestream_entry in ms_entry['bytestreams']:
            presform_ids = []
            if bytestream_entry['type'] == "file content":
                ms.content = LDRPath(bytestream_entry['dst'])
            if bytestream_entry['type'] == "technical metadata":
                ms.add_technicalmetadata(LDRPath(bytestream_entry['dst']))
            if bytestream_entry['type'] == "PREMIS":
                ms.premis = LDRPath(bytestream_entry['dst'])
                premis = PremisRecord(frompath=bytestream_entry['dst'])
                try:
                    relationships = premis.get_object_list()[0].get_relationship()
                except KeyError:
                    relationships = []
                for x in relationships:
                    if x.get_relationshipType() == "derivation" and \
                            x.get_relationshipSubType == "is Source of":
                        presform_ids.append(x.get_relatedObjectIdentifier()[0].\
                                            get_relatedObjectIdentifierValue())
            for x in presform_ids:
                entry = None
                for y in data_manifest['objs']:
                    if x == y['identifier']:
                        entry = y
                ms.add_presform(self._pack_presform_materialsuite(entry,
                                                                  data_manifest))
        return ms

    def _pack_presform_materialsuite(self, ms_entry, data_manifest):
        ms = PresformMaterialSuite()
        premis = None
        for bytestream_entry in ms_entry['bytestreams']:
            presform_ids = []
            if bytestream_entry['type'] == "file content":
                ms.content = LDRPath(bytestream_entry['dst'])
            if bytestream_entry['type'] == "technical metadata":
                ms.add_technicalmetadata(LDRPath(bytestream_entry['dst']))
            if bytestream_entry['type'] == "PREMIS":
                ms.premis = LDRPath(bytestream_entry['dst'])
                premis = PremisRecord(frompath=bytestream_entry['dst'])
                try:
                    relationships = premis.get_object_list()[0].get_relationship()
                except KeyError:
                    relationships = []
                for x in relationships:
                    if x.get_relationshipType() == "derivation" and \
                            x.get_relationshipSubType == "is Source of":
                        presform_ids.append(x.get_relatedObjectIdentifier()[0].\
                                            get_relatedObjectIdentifierValue())
                ext = splitext(premis.get_object_list()[0].get_originalName())
                ms.extension = ext
                for x in presform_ids:
                    entry = None
                    for y in data_manifest['objs']:
                        if x == y['identifier']:
                            entry = y
                    ms.add_presform(self._pack_presform_materialsuite(entry))
        return ms
