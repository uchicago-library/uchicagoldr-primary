import unittest
from os import getcwd
from os.path import isfile, split
from copy import deepcopy

from uchicagoldr.item import Item, AccessionItem
from uchicagoldr.batch import Batch, Directory, AccessionDirectory
from uchicagoldr.bash_cmd import BashCommand


class TestItem(unittest.TestCase):
    def setUp(self):
        self.i = Item(getcwd()+'/1234567890123/testFiles/0.rand')
        self.j = Item(getcwd()+'/1234567890123/testFiles/1.txt')

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

    def testEq(self):
        i_same = Item(getcwd()+'/1234567890123/testFiles/0.rand')
        self.assertTrue(i_same == self.i)
        j_same = Item(getcwd()+'/1234567890123/testFiles/1.txt')
        self.assertTrue(j_same == self.j)
        i_diff = Item(getcwd()+'/0987654321098/testFiles/0.rand')
        self.assertFalse(i_diff == self.i)
        j_diff = Item(getcwd()+'/1234567890123/testFiles/0.rand')
        self.assertFalse(j_diff == self.j)

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


class TestAccessionItem(unittest.TestCase):
    def setUp(self):
        self.i = AccessionItem(getcwd() +
                               '/1234567890123/testFiles/0.rand', getcwd())
        self.j = AccessionItem(getcwd() +
                               '/1234567890123/testFiles/1.txt', getcwd())

    def tearDown(self):
        del(self.i)
        del(self.j)

    def testEq(self):
        self.assertFalse(self.i == self.j)
        i_diff_root = AccessionItem(getcwd() +
                                    '/0987654321098/testFiles/0.rand', getcwd())
        i_diff_acc = AccessionItem(getcwd() +
                                   '/0987654321098/testFiles/0.rand', getcwd(),
                                   accession="different")
        self.assertFalse(self.i == i_diff_root)
        self.assertFalse(self.i == i_diff_acc)
        i_same = AccessionItem(getcwd() +
                               '/1234567890123/testFiles/0.rand', getcwd())
        self.assertTrue(self.i == i_same)

    def testGetSetRootPath(self):
        self.assertEqual(self.i.get_root_path(), getcwd())
        self.assertEqual(self.j.get_root_path(), getcwd())
        self.assertEqual(self.j.get_root_path(),
                         self.i.get_root_path())
        self.i.set_root_path('/new/path')
        self.assertEqual(self.i.get_root_path(), '/new/path')
        self.j.set_root_path('/new/path/again/')
        self.assertEqual(self.j.get_root_path(), '/new/path/again')

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
        self.i.set_canonical_filepath(self.i.find_canonical_filepath())
        self.assertEqual(self.i.get_canonical_filepath(), 'testFiles/0.rand')
        self.j.set_canonical_filepath(self.j.find_canonical_filepath())
        self.assertEqual(self.j.get_canonical_filepath(), 'testFiles/1.txt')

        with self.assertRaises(AssertionError):
            self.i.set_file_path('/new/path/to/file.txt')
            self.i.set_root_path('/new/path/too/deep')
            self.i.find_file_accession()
            self.i.find_canonical_filepath()


class TestBatch(unittest.TestCase):
    def setUp(self):
        self.testBatch1 = Batch()
        self.testBatch2 = Batch()

    def tearDown(self):
        del self.testBatch1
        del self.testBatch2

    def testMint(self):
        self.assertTrue(self.testBatch1)
        self.assertTrue(self.testBatch2)
        self.assertEqual(len(self.testBatch1.get_items()), 0)
        self.assertEqual(len(self.testBatch2.get_items()), 0)

    def testAddGetItem(self):
        i = Item('/legitimate/looking/path.txt')
        j = Item('/another/path')
        self.testBatch1.add_item(i)
        self.assertEqual(self.testBatch1.get_items(), [i])
        self.testBatch1.add_item(j)
        self.assertEqual(self.testBatch1.get_items(), [i, j])

    def testEq(self):
        self.assertTrue(self.testBatch1 == self.testBatch2)
        self.testBatch1.add_item(Item('/abc'))
        self.testBatch2.add_item(Item('/def'))
        self.assertFalse(self.testBatch1 == self.testBatch2)
        new_batch = Batch()
        self.assertFalse(self.testBatch1 == new_batch)
        self.assertFalse(self.testBatch2 == new_batch)
        comp_batch1 = Batch()
        comp_batch2 = Batch()
        comp_batch1.add_item(Item('/random/long/string/for/path'))
        comp_batch2.add_item(Item('/random/long/string/for/path'))
        self.assertEqual(comp_batch1, comp_batch2)

    def testSetItemsIter(self):
        i = Item('/legitimate/looking/path.txt')
        j = Item('/another/path')
        testIter = [i, j]
        self.testBatch1.set_items(testIter)
        self.assertEqual(self.testBatch1.get_items(), [i, j])

    def testSetItemsGen(self):
        i = Item('/legitimate/looking/path.txt')
        j = Item('/another/path')
        testIter = [i, j]
        self.testBatch2.set_items(x for x in testIter)
        iteration = -1
        for item in self.testBatch2.get_items():
            iteration += 1
            self.assertEqual(item, testIter[iteration])


class TestDirectory(unittest.TestCase):
    def setUp(self):
        self.testDirectory1 = Directory(getcwd()+'/1234567890123')

    def tearDown(self):
        del(self.testDirectory1)

    def testMint(self):
        self.assertTrue(self.testDirectory1)
        self.assertEqual(len(self.testDirectory1.get_items()), 0)

    def testEq(self):
        testDir2 = Directory('/not/the/same/path')
        self.assertFalse(self.testDirectory1 == testDir2)
        testDir3 = Directory(getcwd()+'/1234567890123')
        # Not the same item contents
        testDir3.add_item(Item(getcwd()+'/1234567890123/testfakefile.txt'))
        self.assertFalse(self.testDirectory1 == testDir3)
        # No contents
        testDir4 = Directory(getcwd()+'/1234567890123')
        self.assertTrue(self.testDirectory1 == testDir4)
        # Add something...
        self.testDirectory1.add_item(Item(getcwd() +
                                          '/1234567890123/testfakefile.txt'))
        self.assertFalse(self.testDirectory1 == testDir4)

    def testSetGetDirectoryPath(self):
        self.assertEqual(self.testDirectory1.get_directory_path(),
                         getcwd()+'/1234567890123')
        self.testDirectory1.set_directory_path('/new/dir/path')
        self.assertEqual(self.testDirectory1.get_directory_path(),
                         '/new/dir/path')

    def testWalkDirectoryPickingFiles(self):
        i = Item(getcwd() + '/1234567890123/testFiles/0.rand')
        j = Item(getcwd() + '/1234567890123/testFiles/1.txt')
        k = Item(getcwd() + '/1234567890123/testFiles/1.txt.fits.xml')
        l = Item(getcwd() + '/1234567890123/testFiles/testDir/2.csv')
        matches = 0
        for x in self.testDirectory1.walk_directory_picking_files():
            self.assertTrue(x.find_md5_hash() in [i.find_md5_hash(),
                                                  j.find_md5_hash(),
                                                  k.find_md5_hash(),
                                                  l.find_md5_hash()]
                            )
            matches += 1
        self.assertEqual(matches, 4)

    def testAddItem(self):
        i = Item(getcwd()+'/1234567890123/testFiles/0.rand')
        j = Item(getcwd()+'/1234567890123/testFiles/1.txt')
        k = Item(getcwd()+'/1234567890123/testFiles/1.txt.fits.xml')
        l = Item(getcwd()+'/1234567890123/testFiles/testDir/2.csv')
        m = Item('/not/in/the/stated/dirpath')

        self.testDirectory1.add_item(i)
        self.assertEqual(self.testDirectory1.get_items(), [i])
        self.testDirectory1.add_item(j)
        self.assertEqual(self.testDirectory1.get_items(), [i, j])
        self.testDirectory1.add_item(k)
        self.assertEqual(self.testDirectory1.get_items(), [i, j, k])
        self.testDirectory1.add_item(l)
        self.assertEqual(self.testDirectory1.get_items(), [i, j, k, l])
        with self.assertRaises(AssertionError):
            self.testDirectory1.add_item(m)

    def testPopulate(self):
        i = Item(getcwd()+'/1234567890123/testFiles/0.rand')
        j = Item(getcwd()+'/1234567890123/testFiles/1.txt')
        k = Item(getcwd()+'/1234567890123/testFiles/1.txt.fits.xml')
        l = Item(getcwd()+'/1234567890123/testFiles/testDir/2.csv')
        dirContents = [i.find_md5_hash(),
                       j.find_md5_hash(),
                       k.find_md5_hash(),
                       l.find_md5_hash()]
        self.testDirectory1.populate()
        matches = 0
        for entry in self.testDirectory1.get_items():
            matches += 1
            self.assertTrue(entry.find_md5_hash() in dirContents)
        self.assertEqual(matches, 4)


class testAccessionDirectory(unittest.TestCase):
    def setUp(self):
        self.testAccessionDirectory = AccessionDirectory(
            getcwd()+'/1234567890123', getcwd()
        )

    def tearDown(self):
        del self.testAccessionDirectory

    def testMint(self):
        self.assertTrue(self.testAccessionDirectory)

    def testAddGetItem(self):
        self.testAccessionDirectory.add_item(
            AccessionItem(getcwd()+'/1234567890123/testFiles/0.rand', getcwd())
        )

        self.assertEqual(self.testAccessionDirectory.get_items(),
                         [AccessionItem(
                             getcwd()+'/1234567890123/testFiles/0.rand',
                             getcwd()
                         )]
                         )
        self.testAccessionDirectory.add_item(
            AccessionItem(getcwd()+'/1234567890123/testFiles/1.txt', getcwd())
        )

        self.assertEqual(self.testAccessionDirectory.get_items(),
                         [
                             AccessionItem(getcwd() +
                                           '/1234567890123/testFiles/0.rand',
                                           getcwd()),
                             AccessionItem(getcwd() +
                                           '/1234567890123/testFiles/1.txt',
                                           getcwd())
                         ]
                         )

    def testSetGetFindAccession(self):
        self.assertEqual(self.testAccessionDirectory.get_accession(),
                         '1234567890123'
                         )
        self.testAccessionDirectory.set_accession('0987654321098')
        self.assertEqual(self.testAccessionDirectory.get_accession(),
                         '0987654321098'
                         )
        self.testAccessionDirectory.set_accession(
            self.testAccessionDirectory.find_accession_from_relative_path()
        )
        self.assertEqual(self.testAccessionDirectory.get_accession(),
                         '1234567890123'
                         )

    def testGetSetRoot(self):
        self.assertEqual(self.testAccessionDirectory.get_root_path(),
                         getcwd()
                         )

        self.testAccessionDirectory.set_root_path('/new/test/root')
        self.assertEqual(self.testAccessionDirectory.get_root_path(),
                         '/new/test/root'
                         )

    def testWalkDirectoryPickingFiles(self):
        i = AccessionItem(getcwd() + '/1234567890123/testFiles/0.rand',
                          getcwd())
        j = AccessionItem(getcwd() + '/1234567890123/testFiles/1.txt',
                          getcwd())
        k = AccessionItem(getcwd() + '/1234567890123/testFiles/1.txt.fits.xml',
                          getcwd())
        l = AccessionItem(getcwd() + '/1234567890123/testFiles/testDir/2.csv',
                          getcwd())
        matches = 0
        for x in self.testAccessionDirectory.walk_directory_picking_files():
            self.assertTrue(x.find_md5_hash() in [i.find_md5_hash(),
                                                  j.find_md5_hash(),
                                                  k.find_md5_hash(),
                                                  l.find_md5_hash()]
                            )
            matches += 1
        self.assertEqual(matches, 4)

    def testPopulate(self):
        i = AccessionItem(getcwd()+'/1234567890123/testFiles/0.rand',
                          getcwd())
        j = AccessionItem(getcwd()+'/1234567890123/testFiles/1.txt',
                          getcwd())
        k = AccessionItem(getcwd()+'/1234567890123/testFiles/1.txt.fits.xml',
                          getcwd())
        l = AccessionItem(getcwd()+'/1234567890123/testFiles/testDir/2.csv',
                          getcwd())
        dirContents = [i.find_md5_hash(),
                       j.find_md5_hash(),
                       k.find_md5_hash(),
                       l.find_md5_hash()]
        self.testAccessionDirectory.populate()
        matches = 0
        for entry in self.testAccessionDirectory.get_items():
            matches += 1
            self.assertTrue(entry.find_md5_hash() in dirContents)
        self.assertEqual(matches, 4)

    def testEq(self):
        i = AccessionItem(getcwd()+'/1234567890123/testFiles/0.rand',
                          getcwd())
        j = AccessionItem(getcwd()+'/1234567890123/testFiles/1.txt',
                          getcwd())
        k = AccessionItem(getcwd()+'/1234567890123/testFiles/1.txt.fits.xml',
                          getcwd())
        l = AccessionItem(getcwd()+'/1234567890123/testFiles/testDir/2.csv',
                          getcwd())
        blank_same_path = AccessionDirectory(
            getcwd()+'/1234567890123', getcwd()
        )
        self.assertEqual(self.testAccessionDirectory, blank_same_path)
        # Add something
        self.testAccessionDirectory.add_item(i)
        self.assertFalse(self.testAccessionDirectory == blank_same_path)
        # different paths, same children
        diff_path = AccessionDirectory(
            getcwd() + '/1234567890123/testFiles',
            getcwd())
        self.assertFalse(self.testAccessionDirectory == diff_path)
        # different root
        new_root, one_up = split(getcwd())
        diff_root = AccessionDirectory(getcwd() + '/1234567890123',
                                       new_root)
        self.assertFalse(self.testAccessionDirectory == diff_root)

        # And lets just check adding items in sequence...
        # Deep copies of the items for the heck of it
        blank_same_path.add_item(deepcopy(i))
        self.assertEqual(self.testAccessionDirectory, blank_same_path)
        blank_same_path.add_item(deepcopy(j))
        self.assertFalse(self.testAccessionDirectory == blank_same_path)
        self.testAccessionDirectory.add_item(j)
        self.assertEqual(self.testAccessionDirectory, blank_same_path)
        blank_same_path.add_item(deepcopy(k))
        self.assertFalse(self.testAccessionDirectory == blank_same_path)
        self.testAccessionDirectory.add_item(k)
        self.assertEqual(self.testAccessionDirectory, blank_same_path)
        blank_same_path.add_item(deepcopy(l))
        self.assertFalse(self.testAccessionDirectory == blank_same_path)
        self.testAccessionDirectory.add_item(l)
        self.assertEqual(self.testAccessionDirectory, blank_same_path)


class testBashCommand(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()
