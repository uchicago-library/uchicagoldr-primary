import unittest

class TestImports(unittest.TestCase):
    def test_bit_level_imports(self):
        from uchicagoldrtoolsuite.bit_level.impl.filesystemarchivestructurewriter import FileSystemArchiveStructureWriter
        from uchicagoldrtoolsuite.bit_level.impl.filesystemmaterialsuitepackager import FileSystemMaterialSuitePackager
        from uchicagoldrtoolsuite.bit_level.impl.filesystemsegmentpackager import FileSystemSegmentPackager
        from uchicagoldrtoolsuite.bit_level.impl.filesystemstagereader import FileSystemStageReader
        from uchicagoldrtoolsuite.bit_level.impl.filesystemstagewriter import FileSystemStageWriter
        from uchicagoldrtoolsuite.bit_level.impl.ldrpath import LDRPath
        from uchicagoldrtoolsuite.bit_level.impl.ldrurl import LDRURL

        from uchicagoldrtoolsuite.bit_level.lib.absolutefilepathtree import AbsoluteFilePathTree
        from uchicagoldrtoolsuite.bit_level.lib.archivestructure import ArchiveStructure
        from uchicagoldrtoolsuite.bit_level.lib.filepathtree import FilePathTree
        from uchicagoldrtoolsuite.bit_level.lib.filewalker import FileWalker
        from uchicagoldrtoolsuite.bit_level.lib.ldritemoperations import copy
        from uchicagoldrtoolsuite.bit_level.lib.materialsuitepackager import MaterialSuitePackager
        from uchicagoldrtoolsuite.bit_level.lib.materialsuite import MaterialSuite
        from uchicagoldrtoolsuite.bit_level.lib.premisextensionnodes import Restriction
        from uchicagoldrtoolsuite.bit_level.lib.premisobjectrecordcreator import PremisObjectRecordCreator
        from uchicagoldrtoolsuite.bit_level.lib.rootedpath import RootedPath
        from uchicagoldrtoolsuite.bit_level.lib.segmentpackager import SegmentPackager
        from uchicagoldrtoolsuite.bit_level.lib.stageserializationreader import StageSerializationReader
        from uchicagoldrtoolsuite.bit_level.lib.stageserializationwriter import StageSerializationWriter
        from uchicagoldrtoolsuite.bit_level.lib.stage import Stage
        from uchicagoldrtoolsuite.bit_level.lib.technicalmetadatarecordcreator import TechnicalMetadataRecordCreator

        from uchicagoldrtoolsuite.bit_level.lib.abc.ldritem import LDRItem
        from uchicagoldrtoolsuite.bit_level.lib.abc.packager import Packager
        from uchicagoldrtoolsuite.bit_level.lib.abc.serializationreader import SerializationReader
        from uchicagoldrtoolsuite.bit_level.lib.abc.serializationwriter import SerializationWriter
        from uchicagoldrtoolsuite.bit_level.lib.abc.structure import Structure


    def test_core_imports(self):
        from uchicagoldrtoolsuite.core.app.abc.app import App
        from uchicagoldrtoolsuite.core.app.internal.cliapp import CLIApp
        from uchicagoldrtoolsuite.core.app.aru import AccessionRecordEditor
        from uchicagoldrtoolsuite.core.app.postinstall import PostInstall


if __name__ == '__main__':
    unittest.main()
