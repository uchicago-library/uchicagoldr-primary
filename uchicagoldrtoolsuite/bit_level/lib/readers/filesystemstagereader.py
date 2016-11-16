from pathlib import Path
from os import scandir

from pypairtree.utils import path_to_identifier, identifier_to_path

from uchicagoldrtoolsuite.core.lib.convenience import recursive_scandir
from .abc.stageserializationreader import StageSerializationReader
from .abc.segmentpackager import SegmentPackager
from .abc.materialsuitepackager import MaterialSuitePackager
from ..structures.segment import Segment
from ..ldritems.ldrpath import LDRPath


class FileSystemStageReader(StageSerializationReader):
    """
    The reader for pairtree based FileSystem stage structure serializations.
    Given the location of a stage reconstructs the stage structure from byte
    streams serialized as files on disk.
    """
    # TODO: Should this be changed to be more similar to the archive reader,
    # which accepts an environment path and an identifier rather than just a
    # single path? Probably. - BNB
    def __init__(self, path):
        """
        Create a new FileSystemStageReader

        __Args__

        1. path (str): The path to the stage on disk. The leaf component should
            be the stage identifier
        """
        super().__init__()
        self.path = path
        self.struct.set_identifier(str(Path(path).parts[-1]))

    def assert_skeleton(self):
        accessionrecords_dir = Path(self.path, 'admin', 'accessionrecords')
        legalnotes_dir = Path(self.path, 'admin', 'legalnotes')
        adminnotes_dir = Path(self.path, 'admin', 'adminnotes')
        segments_dir = Path(self.path, 'segments')
        for x in [accessionrecords_dir, legalnotes_dir,
                  adminnotes_dir, segments_dir]:
            if not x.is_dir():
                return False
        return True

    def read(self):
        """
        Reads the structure at the given location

        __Returns__

        * self.struct (Stage): The stage
        """
        # If there's not a valid stage skeleton on the file system here return a
        # blank staging structure. Whether or not this should "fail" silently or
        # raise an error might warrant inclusion as a kwarg/CLI flag?
        if not self.assert_skeleton():
            return self.struct

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
    """
    The packager for pairtree based segment serializations

    Given the path and identifier components of a Segment, package that segment
    up and return it
    """
    def __init__(self, path, label_text, label_number):
        """
        Create a new FileSystemSegmentReader

        __Args__

        1. path (str): The path the segment is located at
        2. label_text (str): The textual component of the segment label
        3. label_number (str/int): The numeric component of the segment label
        """
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
        """
        Packages the structure at the given location

        __Returns__

        self.struct (Segment): The segment
        """
        for ident in self._gather_identifiers():
            self.struct.add_materialsuite(
                FileSystemMaterialSuiteReader(
                    self.path,
                    ident
                ).package()
            )
        return self.struct


class FileSystemMaterialSuiteReader(MaterialSuitePackager):
    """
    The packager for pairtree based MaterialSuite serializations

    Given the path where the MaterialSuite is stored, the identifier, and the
    pairtree encapsulation string, packages a MaterialSuite
    """
    def __init__(self, seg_path, identifier, encapsulation='srf'):
        """
        Create a new FileSystemMaterialSuiteReader

        __Args__

        1. seg_path (str): The path to the location where the MaterialSuite
            is stored
        2. identifier (str): The identifier of the MaterialSuite

        __KWArgs__

        * encapsulation (str): The pairtree encapsulation utilized by the
            serializer. Defaults to "srf" for "Stage Resource Folder"
        """
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
