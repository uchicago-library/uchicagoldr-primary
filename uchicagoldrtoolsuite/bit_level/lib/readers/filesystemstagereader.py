from pathlib import Path
from os import scandir

from pypairtree.utils import path_to_identifier, identifier_to_path
from pypremis.lib import PremisRecord

from uchicagoldrtoolsuite.core.lib.convenience import recursive_scandir
from .abc.stageserializationreader import StageSerializationReader
from .abc.segmentpackager import SegmentPackager
from .abc.materialsuitepackager import MaterialSuitePackager
from ..structures.segment import Segment
from ..ldritems.ldrpath import LDRPath


class FileSystemStageReader(StageSerializationReader):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.struct.set_identifier(str(Path(path).parts[-1]))

    def read(self):
        accessionrecords_dir = Path(self.path, 'admin', 'accessionrecords')
        legalnotes_dir = Path(self.path, 'admin', 'legalnotes')
        adminnotes_dir = Path(self.path, 'admin', 'adminnotes')
        segments_dir = Path(self.path, 'segments')

        for x in [x.path for x in scandir(str(accessionrecords_dir))]:
            self.struct.add_accessionrecord(LDRPath(x))
        for x in [x.path for x in scandir(str(legalnotes_dir))]:
            self.struct.add_legalnote(LDRPath(x))
        for x in [x.path for x in scandir(str(adminnotes_dir))]:
            self.struct.add_adminnote(LDRPath(x))
        for x in [x.path for x in scandir(str(segments_dir))]:
            self.struct.add_segment(
                FileSystemSegmentReader(
                    x,
                    str(Path(x).parts[-1]).split("-")[0],
                    str(Path(x).parts[-1]).split("-")[1]
                ).package()
            )
        return self.struct


class FileSystemSegmentReader(SegmentPackager):
    def __init__(self, path, label_text, label_number):
        super().__init__()
        self.path = path
        self.set_struct(Segment(label_text, int(label_number)))

    def _gather_identifiers(self):
        identifiers = []
        for f in recursive_scandir(self.path):
            if not f.is_file():
                continue
            f = f.path
            if not f.endswith("premis.xml"):
                continue
            rel_p = Path(f).relative_to(self.path)
            # remove the file and ecapsulation
            id_dir_path = Path(rel_p.parents[1])
            identifiers.append(path_to_identifier(id_dir_path))
        return identifiers

    def package(self):
        for ident in self._gather_identifiers():
            self.struct.add_materialsuite(
                FileSystemMaterialSuiteReader(
                    self.path,
                    ident
                ).package()
            )
        return self.struct


class FileSystemMaterialSuiteReader(MaterialSuitePackager):
    def __init__(self, seg_path, identifier, encapsulation='srf'):
        super().__init__()
        self.seg_path = seg_path
        self.identifier = identifier
        self.encapsulation = encapsulation
        self.path = Path(self.seg_path, identifier_to_path(identifier),
                         self.encapsulation)

    # Clobber the ABC function here, this is faster and doesn't instantiate
    # a new file for no reason
    def get_identifier(self, _):
        return self.identifier

    def get_content(self):
        p = Path(self.path, 'content.file')
        if p.is_file():
            return LDRPath(str(p))

    def get_premis(self):
        p = Path(self.path, 'premis.xml')
        if p.is_file():
            return LDRPath(str(p))

    def get_techmd_list(self):
        return [LDRPath(x.path) for x in
                scandir(str(Path(self.path, 'TECHMD')))]
