import unittest

class TestImports(unittest.TestCase):
    def test(self):
        from uchicagoldrtoolsuite.bit_level.impl.filesystemarchivestructurewriter import FileSystemArchiveStructureWriter
        from uchicagoldrtoolsuite.bit_level.impl.filesystemmaterialsuitestructurepackager import FileSystemMaterialSuiteStructurePackager
        from uchicagoldrtoolsuite.bit_level.impl.filesystemsegmentstructurepackager import FileSystemSegmentStructurePackager
        from uchicagoldrtoolsuite.bit_level.impl.filesystemstagingstructurereader import FileSystemStagingStructureReader
        from uchicagoldrtoolsuite.bit_level.impl.filesystemstagingstructurewriter import FileSystemStagingStructureWriter
        from uchicagoldrtoolsuite.bit_level.impl.ldrpath import LDRPath
        from uchicagoldrtoolsuite.bit_level.impl.ldrurl import LDRURL


        from uchicagoldrtoolsuite.bit_level.lib.absolutefilepathtree import AbsoluteFilePathTree
        from uchicagoldrtoolsuite.bit_level.lib.archivestructure import ArchiveStructure
        from uchicagoldrtoolsuite.bit_level.lib.filepathtree import FilePathTree
        from uchicagoldrtoolsuite.bit_level.lib.filewalker import FileWalker
        from uchicagoldrtoolsuite.bit_level.lib.ldritemoperations import copy
        from uchicagoldrtoolsuite.bit_level.lib.materialsuitepackager import MaterialSuitePackager
        from uchicagoldrtoolsuite.bit_level.lib.materialsuitestructure import MaterialSuiteStructure
        from uchicagoldrtoolsuite.bit_level.lib.premisextensionnodes import Restriction
        from uchicagoldrtoolsuite.bit_level.lib.premisobjectrecordcreator import PremisObjectRecordCreator
        from uchicagoldrtoolsuite.bit_level.lib.rootedpath import RootedPath
        from uchicagoldrtoolsuite.bit_level.lib.segmentpackager import SegmentPackager
        from uchicagoldrtoolsuite.bit_level.lib.stagingmaterialsuitepackager import StagingMaterialSuitePackager
        from uchicagoldrtoolsuite.bit_level.lib.stagingsegmentpackager import StagingSegmentPackager
        from uchicagoldrtoolsuite.bit_level.lib.stagingserializationreader import StagingSerializationReader
        from uchicagoldrtoolsuite.bit_level.lib.stagingserializationwriter import StagingSerializationWriter
        from uchicagoldrtoolsuite.bit_level.lib.stagingstructure import StagingStructure
        from uchicagoldrtoolsuite.bit_level.lib.technicalmetadatarecordcreator import TechnicalMetadataRecordCreator

        from uchicagoldrtoolsuite.bit_level.lib.abc.ldritem import LDRItem
        from uchicagoldrtoolsuite.bit_level.lib.abc.packager import Packager
        from uchicagoldrtoolsuite.bit_level.lib.abc.serializationreader import SerializationReader
        from uchicagoldrtoolsuite.bit_level.lib.abc.serializationwriter import SerializationWriter
        from uchicagoldrtoolsuite.bit_level.lib.abc.structure import Structure



        from uchicagoldrtoolsuite.core.app.abc.app import App
        from uchicagoldrtoolsuite.core.app.internal.cliapp import CLIApp
        from uchicagoldrtoolsuite.core.app.aru import AccessionRecordEditor
        from uchicagoldrtoolsuite.core.app.postinstall import PostInstall


if __name__ == '__main__':
    unittest.main()
