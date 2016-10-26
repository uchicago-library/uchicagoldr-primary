from os import makedirs as _makedirs
from pathlib import Path
from uuid import uuid4
from json import dump

from pypairtree.utils import identifier_to_path

from .abc.stageserializationwriter import StageSerializationWriter
from ..ldritems.ldrpath import LDRPath
from ..ldritems.ldritemcopier import LDRItemCopier


def makedirs(x):
    _makedirs(x, exist_ok=True)


class PairTreeFileSystemStageWriter(StageSerializationWriter):
    def __init__(self, aStructure, aRoot, eq_detect="bytes"):
        super().__init__(aStructure)
        self.stage_env_path = Path(aRoot)
        self.stage_root = Path(self.stage_env_path, self.struct.identifier)
        self.set_implementation('pairtree filesystem')
        self.eq_detect = eq_detect

    def _build_skeleton(self):
        required_dirs = []
        for x in ['admin', 'segments']:
            required_dirs.append(Path(self.stage_root, x))

        for x in ['accessionrecords', 'adminnotes', 'legalnotes', 'manifests']:
            required_dirs.append(Path(self.stage_root, 'admin', x))

        for x in required_dirs:
            makedirs(str(x))

    def _write_accessionrecords(self):
        for x in self.struct.accessionrecord_list:
            if x.item_name:
                item_name = x.item_name
            else:
                item_name = uuid4().hex
            target_path = Path(self.stage_root, 'admin',
                               'accessionrecords', item_name)
            target_item = LDRPath(str(target_path))
            copier = LDRItemCopier(x, target_item, eq_detect=self.eq_detect)
            copier.copy()

    def _write_adminnotes(self):
        for x in self.struct.adminnote_list:
            if x.item_name:
                item_name = x.item_name
            else:
                item_name = uuid4().hex
            target_path = Path(self.stage_root, 'admin',
                               'adminnotes', item_name)
            target_item = LDRPath(str(target_path))
            copier = LDRItemCopier(x, target_item, eq_detect=self.eq_detect)
            cr = copier.copy()
            if not cr['src_eqs_dst']:
                raise ValueError()

    def _write_legalnotes(self):
        for x in self.struct.legalnote_list:
            if x.item_name:
                item_name = x.item_name
            else:
                item_name = uuid4().hex
            target_path = Path(self.stage_root, 'admin',
                               'legalnotes', item_name)
            target_item = LDRPath(str(target_path))
            copier = LDRItemCopier(x, target_item, eq_detect=self.eq_detect)
            cr = copier.copy()
            if not cr['src_eqs_dst']:
                raise ValueError()

    def write(self):
        self._build_skeleton()
        self._write_accessionrecords()
        self._write_adminnotes()
        self._write_legalnotes()
        for x in self.struct.segment_list:
            ptfssw = PairTreeFileSystemSegmentWriter(
                x, str(Path(self.stage_root, 'segments')),
                eq_detect=self.eq_detect
            )
            ptfssw.write()


class PairTreeFileSystemSegmentWriter(object):
    def __init__(self, aStructure, aRoot, eq_detect="bytes"):
        self.struct = aStructure
        self.segment_root = Path(aRoot, self.struct.identifier)
        self.eq_detect = eq_detect

    def _write_skeleton(self):
#        materialsuites_root = Path(self.segment_root, 'materialsuites')
        materialsuites_root = self.segment_root
        makedirs(str(materialsuites_root))

#    def _write_manifest(self):
#        with open(str(Path(self.segment_root, 'manifest.json')), 'w') as f:
#            dump(
#                [x.identifier for x in self.struct.materialsuite_list],
#                f,
#                ident=4
#            )

    def write(self):
        self._write_skeleton()
#        self._write_manifest()
        for x in self.struct.materialsuite_list:
            ptfsmsw = PairTreeFileSystemMaterialSuiteWriter(
                x,
#                str(Path(self.segment_root, 'materialsuites')),
                str(self.segment_root),
                eq_detect=self.eq_detect
            )
            ptfsmsw.write()


class PairTreeFileSystemMaterialSuiteWriter(object):
    def __init__(self, aStructure, aRoot, eq_detect="bytes"):
        self.struct = aStructure
        self.materialsuite_root = Path(
            identifier_to_path(self.struct.identifier, root=aRoot),
            "srf"
        )
        self.eq_detect = eq_detect

    def _write_skeleton(self):
        makedirs(str(Path(self.materialsuite_root, 'TECHMD')))

    def write(self):
        self._write_skeleton()
        target_content_path = Path(self.materialsuite_root, 'content.file')
        target_content_item = LDRPath(str(target_content_path))
        target_premis_path = Path(self.materialsuite_root, 'premis.xml')
        target_premis_item = LDRPath(str(target_premis_path))

        copiers = []
        copiers.append(LDRItemCopier(self.struct.content, target_content_item))
        copiers.append(LDRItemCopier(self.struct.premis, target_premis_item))

        for x in self.struct.technicalmetadata_list:
            if x.item_name:
                item_name = x.item_name
            else:
                item_name = uuid4().hex
            target_techmd_path = Path(self.materialsuite_root,
                                      'TECHMD', item_name)
            target_techmd_item = LDRPath(str(target_techmd_path))
            copiers.append(LDRItemCopier(x, target_techmd_item))

        for x in copiers:
            cr = x.copy()
            if not cr['src_eqs_dst']:
                raise ValueError()
