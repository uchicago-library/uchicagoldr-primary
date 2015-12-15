import unittest
from os import getcwd
from os.path import isfile

from uchicagoldr.item import Item
from uchicagoldr.batch import Batch
from uchicagoldr.bash_cmd import BashCommand


class TestItem(unittest.TestCase):
    def setUp(self):
        self.i = Item(getcwd()+'/1234567890123/testFiles/0.rand', getcwd())
        self.j = Item(getcwd()+'/1234567890123/testFiles/1.txt', getcwd()+"/")

    def tearDown(self):
        del(self.i)
        del(self.j)

    def testMint(self):
        self.assertTrue(self.i)
        self.assertTrue(self.j)

    def testTestReadability(self):
        self.assertTrue(self.i.test_readability())
        self.assertTrue(self.j.test_readability())

    def testGetSetFilePath(self):
        self.assertEqual(self.i.get_file_path(),
                         getcwd()+'/1234567890123/testFiles/0.rand')
        self.assertTrue(isfile(self.i.get_file_path()))
        self.assertEqual(self.j.get_file_path(),
                         getcwd()+'/1234567890123/testFiles/1.txt')
        self.assertTrue(isfile(self.j.get_file_path()))
        self.i.set_file_path('/new/path')
        self.assertEqual(self.i.get_file_path(), '/new/path')
        self.j.set_file_path('/new/path/again/')
        self.assertEqual(self.j.get_file_path(), '/new/path/again')

        with self.assertRaises(AssertionError):
            self.j.set_file_path('this isn\'t a valid filepath')
        with self.assertRaises(AssertionError):
            self.i.set_file_path('this/is/more/convincing')

    def testGetSetRootPath(self):
        self.assertEqual(self.i.get_root_path(), getcwd())
        self.assertEqual(self.j.get_root_path(), getcwd())
        self.assertEqual(self.j.get_root_path(),
                         self.i.get_root_path())
        self.i.set_root_path('/new/path')
        self.assertEqual(self.i.get_root_path(), '/new/path')
        self.j.set_root_path('/new/path/again/')
        self.assertEqual(self.j.get_root_path(), '/new/path/again')

    def testSetGetFindMD5(self):
        self.i.set_md5(self.i.find_md5_hash())
        self.assertEqual(self.i.get_md5(), 'c00ecc4e3efa25d17842217b57e999dd')
        self.j.set_md5(self.j.find_md5_hash())
        self.assertEqual(self.j.get_md5(), 'd03fd97600532ef84ddc1e578ea843e9')

    def testSetGetFindSHA(self):
        self.i.set_sha256(self.i.find_sha256_hash())
        self.assertEqual(
            self.i.get_sha256(),
            '7edd27408a15d28d96874938ff7211d3591f301c52c0cc5fd2483d25afc5ad90'
        )
        self.j.set_sha256(self.j.find_sha256_hash())
        self.assertEqual(
            self.j.get_sha256(),
            'a7a3d006d0b37872526f57529014864b1da514e9e00799eb4f8b71d080c5a9a6'
        )

    def testSetGetFindAccession(self):
        self.i.set_accession(self.i.find_file_accession())
        self.assertEqual(self.i.get_accession(), '1234567890123')
        self.j.set_accession(self.j.find_file_accession())
        self.assertEqual(self.j.get_accession(), '1234567890123')

        self.i.set_accession('0987654321098')
        self.assertEqual(self.i.get_accession(), '0987654321098')

        with self.assertRaises(ValueError):
            self.j.set_accession('1')

    def testSetGetFindCannonicalPath(self):
        with self.assertRaises(AssertionError):
            self.i.find_canonical_filepath()
        self.i.set_accession(self.i.find_file_accession())
        self.j.set_accession(self.j.find_file_accession())
        self.i.set_canonical_filepath(self.i.find_canonical_filepath())
        self.assertEqual(self.i.get_canonical_filepath(), 'testFiles/0.rand')
        self.j.set_canonical_filepath(self.j.find_canonical_filepath())
        self.assertEqual(self.j.get_canonical_filepath(), 'testFiles/1.txt')

        with self.assertRaises(AssertionError):
            self.i.set_file_path('/new/path/to/file.txt')
            self.i.set_root_path('/new/path/too/deep')
            self.i.find_file_accession()
            self.i.find_canonical_filepath()

    def testSetGetFindMime(self):
        self.i.set_file_mime_type(self.i.find_file_mime_type())
        self.assertEqual(self.i.get_file_mime_type(),
                         'application/octet-stream')
        self.j.set_file_mime_type(self.j.find_file_mime_type())
        self.assertEqual(self.j.get_file_mime_type(),
                         "text/plain")

    def testFindFileName(self):
        self.assertEqual(self.i.find_file_name(), '0.rand')
        self.assertEqual(self.j.find_file_name(), '1.txt')

    def testFindFileNameNoExtension(self):
        self.assertEqual(self.i.find_file_name_no_extension(), '0')
        self.assertEqual(self.j.find_file_name_no_extension(), '1')

        self.i.set_file_path('/test/name/with.several.dots')
        self.assertEqual(self.i.find_file_name_no_extension(), 'with.several')

    def testSetGetFindFileExtension(self):
        self.i.set_file_extension(self.i.find_file_extension())
        self.assertEqual(self.i.get_file_extension(), '.rand')
        self.j.set_file_extension(self.j.find_file_extension())
        self.assertEqual(self.j.get_file_extension(), '.txt')

    def testFindGetSetFileSize(self):
        self.i.set_file_size(self.i.find_file_size())
        self.assertEqual(self.i.get_file_size(), 1048576)
        self.j.set_file_size(self.j.find_file_size())
        self.assertEqual(self.j.get_file_size(), 20)

    def testFindTechnicalMetadata(self):
        self.assertFalse(self.i.find_technical_metadata())
        self.assertTrue(self.j.find_technical_metadata())


class testBatch(unittest.TestCase):
    pass


class testBashCommand(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()
