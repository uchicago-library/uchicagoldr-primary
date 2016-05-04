import unittest

from uchicagoldrtoolsuite.bit_level.lib.filesystemarchivestructurewriter import FileSystemArchiveStructureWriter
from uchicagoldrtoolsuite.bit_level.lib.filesystemmaterialsuitepackager import FileSystemMaterialSuitePackager
from uchicagoldrtoolsuite.bit_level.lib.filesystemsegmentpackager import FileSystemSegmentPackager
from uchicagoldrtoolsuite.bit_level.lib.filesystemstagereader import FileSystemStageReader
from uchicagoldrtoolsuite.bit_level.lib.filesystemstagewriter import FileSystemStageWriter
from uchicagoldrtoolsuite.bit_level.lib.ldrpath import LDRPath
from uchicagoldrtoolsuite.bit_level.lib.ldrurl import LDRURL

from uchicagoldrtoolsuite.bit_level.lib.absolutefilepathtree import AbsoluteFilePathTree
from uchicagoldrtoolsuite.bit_level.lib.archivestructure import ArchiveStructure
from uchicagoldrtoolsuite.bit_level.lib.filepathtree import FilePathTree
from uchicagoldrtoolsuite.bit_level.lib.filewalker import FileWalker
from uchicagoldrtoolsuite.bit_level.lib.ldritemoperations import copy
from uchicagoldrtoolsuite.bit_level.lib.abc.materialsuitepackager import MaterialSuitePackager
from uchicagoldrtoolsuite.bit_level.lib.materialsuite import MaterialSuite
from uchicagoldrtoolsuite.bit_level.lib.premisextensionnodes import Restriction
from uchicagoldrtoolsuite.bit_level.lib.premisobjectrecordcreator import PremisObjectRecordCreator
from uchicagoldrtoolsuite.bit_level.lib.rootedpath import RootedPath
from uchicagoldrtoolsuite.bit_level.lib.abc.segmentpackager import SegmentPackager
from uchicagoldrtoolsuite.bit_level.lib.abc.stageserializationreader import StageSerializationReader
from uchicagoldrtoolsuite.bit_level.lib.abc.stageserializationwriter import StageSerializationWriter
from uchicagoldrtoolsuite.bit_level.lib.stage import Stage
from uchicagoldrtoolsuite.bit_level.lib.segment import Segment
from uchicagoldrtoolsuite.bit_level.lib.technicalmetadatarecordcreator import TechnicalMetadataRecordCreator

from uchicagoldrtoolsuite.bit_level.lib.abc.ldritem import LDRItem
from uchicagoldrtoolsuite.bit_level.lib.abc.abc.packager import Packager
from uchicagoldrtoolsuite.bit_level.lib.abc.abc.serializationreader import SerializationReader
from uchicagoldrtoolsuite.bit_level.lib.abc.abc.serializationwriter import SerializationWriter
from uchicagoldrtoolsuite.bit_level.lib.abc.structure import Structure


from uchicagoldrtoolsuite.core.app.abc.app import App
from uchicagoldrtoolsuite.core.app.internal.cliapp import CLIApp
from uchicagoldrtoolsuite.core.app.aru import AccessionRecordEditor
from uchicagoldrtoolsuite.core.app.postinstall import PostInstall

class TestStructures(unittest.TestCase):
    def testStage(self):
        x = Stage('stage id')
        inheritance_tree = [
            Structure,
            Stage
        ]
        for parent in inheritance_tree:
            self.assertTrue(isinstance(x, parent))
        self.assertTrue(type(x) == inheritance_tree[-1])

    def testSegment(self):
        x = Segment('prefix', 2)
        inheritance_tree = [
            Structure,
            Segment
        ]
        for parent in inheritance_tree:
            self.assertTrue(isinstance(x, parent))
        self.assertTrue(type(x) == inheritance_tree[-1])

    def testMaterialSuite(self):
        x = MaterialSuite('someid')
        inheritance_tree = [
            Structure,
            MaterialSuite
        ]
        for parent in inheritance_tree:
            self.assertTrue(isinstance(x, parent))
        self.assertTrue(type(x) == inheritance_tree[-1])

    def testArchiveStructure(self):
        x = ArchiveStructure('someid')
        inheritance_tree = [
            Structure,
            ArchiveStructure
        ]
        for parent in inheritance_tree:
            self.assertTrue(isinstance(x, parent))
        self.assertTrue(type(x) == inheritance_tree[-1])


class TestLDRItems(unittest.TestCase):
    def testLDRPath(self):
        x = LDRPath('/made/up/path.txt')
        inheritance_tree = [
            LDRItem,
            LDRPath
        ]
        for parent in inheritance_tree:
            self.assertTrue(isinstance(x, parent))
        self.assertTrue(type(x) == inheritance_tree[-1])

    def testLDRURL(self):
        x = LDRURL('http://www.definitelynotarealurlprobably.com/1.jpg')
        inheritance_tree = [
            LDRItem,
            LDRURL
        ]
        for parent in inheritance_tree:
            self.assertTrue(isinstance(x, parent))
        self.assertTrue(type(x) == inheritance_tree[-1])


class TestPackagers(unittest.TestCase):
    def testFileSystemMaterialSuitePackager(self):
        x = FileSystemMaterialSuitePackager()
        inheritance_tree = [
            Packager,
            MaterialSuitePackager,
            FileSystemMaterialSuitePackager
        ]
        for parent in inheritance_tree:
            self.assertTrue(isinstance(x, parent))
        self.assertTrue(type(x) == inheritance_tree[-1])

    def testFileSystemSegmentPackager(self):
        x = FileSystemSegmentPackager('label', 6)
        inheritance_tree = [
            Packager,
            SegmentPackager,
            FileSystemSegmentPackager,
        ]
        for parent in inheritance_tree:
            self.assertTrue(isinstance(x, parent))
        self.assertTrue(type(x) == inheritance_tree[-1])


class TestSerializationReaders(unittest.TestCase):
    def testFileSystemStageReader(self):
        x = FileSystemStageReader('/some/path')
        inheritance_tree = [
            SerializationReader,
            StageSerializationReader,
            FileSystemStageReader
        ]
        for parent in inheritance_tree:
            self.assertTrue(isinstance(x, parent))
        self.assertTrue(type(x) == inheritance_tree[-1])


class TestSerializationWriters(unittest.TestCase):
    def testFileSystemStageWriter(self):
        x = FileSystemStageWriter(FileSystemStageReader('/not/real/').read())
        inheritance_tree = [
            SerializationWriter,
            StageSerializationWriter,
            FileSystemStageWriter
        ]
        for parent in inheritance_tree:
            self.assertTrue(isinstance(x, parent))
        self.assertTrue(type(x) == inheritance_tree[-1])


if __name__ == '__main__':
    unittest.main()
