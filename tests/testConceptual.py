import unittest
from uchicagoldr.keyvaluepair import KeyValuePair as KVP
from uchicagoldr.keyvaluepairlist import KeyValuePairList as KVPList
from uchicagoldr.family import Family
from uchicagoldr.filepointer import FilePointer


class TestKeyValuePair(unittest.TestCase):
    def testMintSingle(self):
        kvp = KVP('test key', 'test value')
        self.assertTrue(kvp)

    def testMintMany(self):
        many = []
        for i in range(100):
            kvp = KVP('key_'+str(i), 'value_'+str(i))
            self.assertTrue(kvp)
            many.append(kvp)
        self.assertEqual(len(many), 100)

    def testJustKey(self):
        kvp = KVP('key')
        self.assertTrue(kvp)

    def testGoodKey(self):
        kvp = KVP('this key is a string', 'test value')
        self.assertTrue(kvp)
        kvp = KVP('this key is still a string', 5)
        self.assertTrue(kvp)

    def testBadKey(self):
        with self.assertRaises(TypeError):
            kvp = KVP(1, 'test')
        with self.assertRaises(TypeError):
            kvp = KVP([], 'test')
        with self.assertRaises(TypeError):
            kvp = KVP({}, 'test')
        with self.assertRaises(TypeError):
            kvp = KVP(float(1), 'test')

    def testBadValue(self):
        with self.assertRaises(TypeError):
            kvp = KVP('test', [])
        with self.assertRaises(TypeError):
            kvp = KVP('test', {})
        with self.assertRaises(TypeError):
            kvp = KVP('test', KVP())

    def testGoodValueStr(self):
        kvp = KVP('test', 'string')
        self.assertTrue(kvp)

    def testgoodValueInt(self):
        kvp = KVP('test', 1)
        self.assertTrue(kvp)

    def testGoodValueFloat(self):
        kvp = KVP('test', float(1))
        self.assertTrue(kvp)

    def testGoodValueComplex(self):
        kvp = KVP('test', complex(1))
        self.assertTrue(kvp)

    def testEqual(self):
        kvp1 = KVP('this', 'that')
        kvp2 = KVP('this', 'that')
        kvp3 = KVP('test', 1)
        kvp4 = KVP('test', 1)
        self.assertTrue((kvp1 == kvp2) and (kvp3 == kvp4))

    def testNotEqual(self):
        kvp1 = KVP('this', 'that')
        kvp2 = KVP('this', 'again')
        kvp3 = KVP('test', 1)
        self.assertFalse(kvp1 == kvp3)
        self.assertFalse(kvp1 == kvp2)

    def testGetKey(self):
        kvp1 = KVP('test_key', 'test_value')
        self.assertEqual(kvp1.get_key(), 'test_key')

    def testGetValue(self):
        kvp1 = KVP('test_key', 'test_value')
        self.assertEqual(kvp1.get_value(), 'test_value')
        kvp2 = KVP('test_nested_key', 'test_nested_value')
        kvps = KVPList()
        kvps.append(kvp2)
        kvp3 = KVP('test_nest', kvps)
        self.assertTrue(kvp3.get_value())

    def testNestedDetection(self):
        kvp2 = KVP('test_nested_key', 'test_nested_value')
        kvps = KVPList()
        kvps.append(kvp2)
        kvp3 = KVP('test_nest', kvps)
        self.assertTrue(kvp3)
        self.assertTrue(kvp3.nested)

    def testGetNested(self):
        kvp2 = KVP('test_nested_key', 'test_nested_value')
        kvps = KVPList()
        kvps.append(kvp2)
        kvp3 = KVP('test_nest', kvps)
        self.assertTrue(kvp3)
        self.assertTrue(kvp3.is_nested())
        kvp4 = KVP('test', 'test')
        self.assertFalse(kvp4.is_nested())

    def testCollisions(self):
        pass


class testKeyValuePairList(unittest.TestCase):
    def testMint(self):
        kvp = KVP('test', 'test')
        kvps = KVPList()
        kvps.append(kvp)
        self.assertTrue(kvps)

    def testEmpty(self):
        kvps = KVPList()
        self.assertFalse(kvps)

    def testNest(self):
        kvp1 = KVP('testkey1', 'testvalue1')
        kvp2 = KVP('testkey2', 'testvalue2')
        kvp3 = KVP('testkey3', 'testvalue3')

        kvps1 = KVPList()
        kvps2 = KVPList()
        kvps3 = KVPList()

        kvp_nest = KVP('testnest', kvps3)

        kvps1.append(kvp1)
        kvps2.append(kvp2)
        kvps3.append(kvp3)

        kvps1.append(kvp_nest)

        self.assertTrue(kvps1)

    def testRecursionError(self):
        kvp1 = KVP('testkey1', 'testvalue1')
        kvp2 = KVP('testkey2', 'testvalue2')
        kvp3 = KVP('testkey3', 'testvalue3')

        kvps1 = KVPList()
        kvps2 = KVPList()
        kvps3 = KVPList()

        kvp_nest = KVP('testnest', kvps3)

        kvps1.append(kvp1)
        kvps2.append(kvp2)
        kvps3.append(kvp3)

        with self.assertRaises(RecursionError):
            kvps3.append(kvp_nest)


class testFamily(unittest.TestCase):
    def setUp(self):
        self.families = []
        self.family10 = Family(descs=KVPList([KVP('10', '10')]))
        self.families.append(self.family10)
        self.family9 = Family(descs=KVPList([KVP('9', '9')]))
        self.families.append(self.family9)
        self.family8 = Family(descs=KVPList([KVP('8', '8')]))
        self.families.append(self.family8)
        self.family7 = Family(descs=KVPList([KVP('7', '7')]))
        self.families.append(self.family7)
        self.family6 = Family(descs=KVPList([KVP('6', '6')]))
        self.families.append(self.family6)
        self.family5 = Family(descs=KVPList([KVP('5', '5')]))
        self.families.append(self.family5)
        self.family4 = Family(descs=KVPList([KVP('4', '4')]))
        self.families.append(self.family4)
        self.family3 = Family(descs=KVPList([KVP('3', '3')]))
        self.families.append(self.family3)
        self.family2 = Family(descs=KVPList([KVP('2', '2')]))
        self.families.append(self.family2)
        self.family1 = Family(descs=KVPList([KVP('1', '1')]))
        self.families.append(self.family1)

        self.filePointers = []
        self.filePointer1 = FilePointer('1')
        self.filePointers.append(self.filePointer1)
        self.filePointer2 = FilePointer('2')
        self.filePointers.append(self.filePointer1)
        self.filePointer3 = FilePointer('3')
        self.filePointers.append(self.filePointer1)
        self.filePointer4 = FilePointer('4')
        self.filePointers.append(self.filePointer1)
        self.filePointer5 = FilePointer('5')
        self.filePointers.append(self.filePointer1)
        self.filePointer6 = FilePointer('6')
        self.filePointers.append(self.filePointer1)
        self.filePointer7 = FilePointer('7')
        self.filePointers.append(self.filePointer1)
        self.filePointer8 = FilePointer('8')
        self.filePointers.append(self.filePointer1)
        self.filePointer9 = FilePointer('9')
        self.filePointers.append(self.filePointer1)
        self.filePointer10 = FilePointer('10')
        self.filePointers.append(self.filePointer1)

    def tearDown(self):
        del self.family1
        del self.family2
        del self.family3
        del self.family4
        del self.family5
        del self.family6
        del self.family7
        del self.family8
        del self.family9
        del self.family10
        del self.families

    def testMint(self):
        test = Family()
        self.assertTrue(test)

    def testGetUUID(self):
        test = Family()
        self.assertTrue(test.get_uuid())

    def testMintMany(self):
        tests = []
        uuids = []
        for i in range(100):
            test = Family()
            tests.append(test)
        for family in tests:
            self.assertTrue(family.get_uuid() not in uuids)
            self.assertTrue(family == tests[0])

    def testInitChildrenAndDescs(self):
        self.family10 = Family(descs=KVPList([KVP('10', '10')]),children=[self.filePointer1])
        self.family9 = Family(descs=KVPList([KVP('9', '9')]),children=[self.filePointer2])
        self.family8 = Family(descs=KVPList([KVP('8', '8')]),children=[self.filePointer3])
        self.family7 = Family(descs=KVPList([KVP('7', '7')]),children=[self.filePointer4])
        self.family6 = Family(descs=KVPList([KVP('6', '6')]),children=[self.filePointer5])
        self.family5 = Family(descs=KVPList([KVP('5', '5')]),children=[self.filePointer6])
        self.family4 = Family(descs=KVPList([KVP('4', '4')]),
                              children=[self.family9, self.family10, self.filePointer7])
        self.family3 = Family(descs=KVPList([KVP('3', '3')]),
                              children=[self.family7, self.family8, self.filePointer8])
        self.family2 = Family(descs=KVPList([KVP('2', '2')]),
                              children=[self.family5, self.family6, self.filePointer9])
        self.family1 = Family(descs=KVPList([KVP('1', '1')]),
                              children=[self.family2, self.family3,
                                        self.family4, self.filePointer10])

        self.assertEqual(len(self.family1.children), 4)
        self.assertEqual(len(self.family2.children), 3)
        self.assertEqual(len(self.family3.children), 3)
        self.assertEqual(len(self.family4.children), 3)
        self.assertEqual(len(self.family5.children), 1)
        self.assertEqual(len(self.family6.children), 1)
        self.assertEqual(len(self.family7.children), 1)
        self.assertEqual(len(self.family8.children), 1)
        self.assertEqual(len(self.family9.children), 1)
        self.assertEqual(len(self.family10.children), 1)

    def testAddChild(self):
        self.family1.add_child(self.family2)
        self.family1.add_child(self.family3)
        self.family1.add_child(self.family4)
        self.family2.add_child(self.family5)
        self.family2.add_child(self.family6)
        self.family3.add_child(self.family7)
        self.family3.add_child(self.family8)
        self.family4.add_child(self.family9)
        self.family4.add_child(self.family10)

        self.assertEqual(len(self.family1.children), 3)
        self.assertEqual(len(self.family2.children), 2)
        self.assertEqual(len(self.family3.children), 2)
        self.assertEqual(len(self.family4.children), 2)
        self.assertEqual(len(self.family5.children), 0)
        self.assertEqual(len(self.family6.children), 0)
        self.assertEqual(len(self.family7.children), 0)
        self.assertEqual(len(self.family8.children), 0)
        self.assertEqual(len(self.family9.children), 0)
        self.assertEqual(len(self.family10.children), 0)

    def testAddGetDesc(self):
        self.family10 = Family()
        self.family9 = Family()
        self.family8 = Family()
        self.family7 = Family()
        self.family6 = Family()
        self.family5 = Family()
        self.family4 = Family(
                              children=[self.family9, self.family10])
        self.family3 = Family(
                              children=[self.family7, self.family8])
        self.family2 = Family(
                              children=[self.family5, self.family6])
        self.family1 = Family(
                              children=[self.family2, self.family3,
                                        self.family4])

        self.kvps = []
        for i in range(1, 11):
            self.kvp = KVP('key_'+str(i), 'value_'+str(i))
            self.kvps.append(self.kvp)

        self.family1.add_desc(self.kvps[0])
        self.family2.add_desc(self.kvps[1])
        self.family3.add_desc(self.kvps[2])
        self.family4.add_desc(self.kvps[3])
        self.family5.add_desc(self.kvps[4])
        self.family6.add_desc(self.kvps[5])
        self.family7.add_desc(self.kvps[6])
        self.family8.add_desc(self.kvps[7])
        self.family9.add_desc(self.kvps[8])
        self.family10.add_desc(self.kvps[9])

        self.assertEqual(self.family1.get_descs(), [KVP('key_1', 'value_1')])
        self.assertEqual(self.family2.get_descs(), [KVP('key_2', 'value_2')])
        self.assertEqual(self.family3.get_descs(), [KVP('key_3', 'value_3')])
        self.assertEqual(self.family4.get_descs(), [KVP('key_4', 'value_4')])
        self.assertEqual(self.family5.get_descs(), [KVP('key_5', 'value_5')])
        self.assertEqual(self.family6.get_descs(), [KVP('key_6', 'value_6')])
        self.assertEqual(self.family7.get_descs(), [KVP('key_7', 'value_7')])
        self.assertEqual(self.family8.get_descs(), [KVP('key_8', 'value_8')])
        self.assertEqual(self.family9.get_descs(), [KVP('key_9', 'value_9')])
        self.assertEqual(self.family10.get_descs(), [KVP('key_10', 'value_10')])

    def testRemoveChildByIndex(self):
        self.family1.add_child(self.family2)
        self.family1.add_child(self.family3)
        self.family1.add_child(self.family4)
        self.family2.add_child(self.family5)
        self.family2.add_child(self.family6)
        self.family3.add_child(self.family7)
        self.family3.add_child(self.family8)
        self.family4.add_child(self.family9)
        self.family4.add_child(self.family10)
        self.family4.remove_child_by_index(0)
        for child in self.family4.get_children():
            self.assertEqual(child, self.family10)

    def testRemoveChild(self):
        self.family1.add_child(self.family2)
        self.family1.add_child(self.family3)
        self.family1.add_child(self.family4)
        self.family2.add_child(self.family5)
        self.family2.add_child(self.family6)
        self.family3.add_child(self.family7)
        self.family3.add_child(self.family8)
        self.family4.add_child(self.family9)
        self.family4.add_child(self.family10)

        self.family4.remove_child(self.family9)
        for child in self.family4.get_children():
            self.assertEqual(child, self.family10)

    def testInfinFamilyDetect(self):
        self.family1.add_child(self.family2)
        self.family1.add_child(self.family3)
        self.family1.add_child(self.family4)
        self.family2.add_child(self.family5)
        self.family2.add_child(self.family6)
        self.family3.add_child(self.family7)
        self.family3.add_child(self.family8)
        self.family4.add_child(self.family9)
        self.family4.add_child(self.family10)
        with self.assertRaises(RecursionError):
            self.family5.add_child(self.family2)
        with self.assertRaises(RecursionError):
            self.family8.add_child(self.family1)

    def testSetChildren(self):
        testSet1 = [self.family2, self.family3]
        testSet2 = [self.family3, self.family4]

        self.family1.set_children(testSet1)
        self.assertTrue(self.family1.get_children() == testSet1)

        self.family1.set_children(testSet2)
        self.assertTrue(self.family1.get_children() == testSet2)

    def testFamilyPrint(self):
        self.family1.add_child(self.family2)
        self.family1.add_child(self.family3)
        self.family1.add_child(self.family4)
        self.family2.add_child(self.family5)
        self.family2.add_child(self.family6)
        self.family3.add_child(self.family7)
        self.family3.add_child(self.family8)
        self.family4.add_child(self.family9)
        self.family4.add_child(self.family10)

        self.assertEqual(len(self.family1.children), 3)
        self.assertEqual(len(self.family2.children), 2)
        self.assertEqual(len(self.family3.children), 2)
        self.assertEqual(len(self.family4.children), 2)
        self.assertEqual(len(self.family5.children), 0)
        self.assertEqual(len(self.family6.children), 0)
        self.assertEqual(len(self.family7.children), 0)
        self.assertEqual(len(self.family8.children), 0)
        self.assertEqual(len(self.family9.children), 0)
        self.assertEqual(len(self.family10.children), 0)
        self.assertTrue(self.family1.__repr__())
        self.assertTrue(self.family1.__str__())

    def testFamilyRawWriteToDisk(self):
        from os import getcwd, remove
        from os.path import join, exists

        self.family1.write_to_file()

        self.assertTrue(exists(
            join(getcwd(), self.family1.get_uuid()+'.family')))
        remove(join(getcwd(), self.family1.get_uuid()+'.family'))

    def testFamilyRawReadFromDisk(self):
        from os import getcwd, remove
        from os.path import join
        from pickle import load

        self.family1 = Family(descs=KVPList([KVP('writetest', 'writetest')]))
        self.family1.write_to_file()
        with open(join(getcwd(), self.family1.get_uuid()+'.family'), 'rb') as f:
            self.family_comp = load(f)
        self.assertTrue(self.family1 == self.family_comp)
        remove(join(getcwd(), self.family1.get_uuid()+'.family'))

    def testFamilyFlatten(self):
        self.family1.add_child(self.family2)
        self.family1.add_child(self.family3)
        self.family1.add_child(self.family4)
        self.family2.add_child(self.family5)
        self.family2.add_child(self.family6)
        self.family3.add_child(self.family7)
        self.family3.add_child(self.family8)
        self.family4.add_child(self.family9)
        self.family4.add_child(self.family10)

        self.family1.flatten()
        self.assertEqual(self.family1.get_children(),
                         [self.family2.get_uuid(), self.family3.get_uuid(),
                          self.family4.get_uuid()])

#    def testFamilyWriteToDir(self):
#        from os.path import isfile, join
#        from os import getcwd, remove
#        self.family1.add_child(self.family2)
#        self.family1.add_child(self.family3)
#        self.family1.add_child(self.family4)
#        self.family2.add_child(self.family5)
#        self.family2.add_child(self.family6)
#        self.family3.add_child(self.family7)
#        self.family3.add_child(self.family8)
#        self.family4.add_child(self.family9)
#        self.family4.add_child(self.family10)
#        self.family1.write_to_dir()
#        self.filenames = [x.get_uuid() for x in self.families]
#        # This should be made recursive in the future.
#        # The test struct is only 2 deep
#        for x in [self.filenames[9]]:
#            self.assertTrue(isfile(join(getcwd(), "0_"+x+'.family')))
#            remove(join(getcwd(),"0_"+x+'.family'))
#        for x in [self.filenames[8], self.filenames[7], self.filenames[6]]:
#            self.assertTrue(isfile(join(getcwd(), "1_"+x+'.family')))
#            remove(join(getcwd(),"1_"+x+'.family'))
#        for x in [self.filenames[5], self.filenames[4], self.filenames[3],
#                  self.filenames[2], self.filenames[1], self.filenames[0]]:
#            self.assertTrue(isfile(join(getcwd(), "2_"+x+'.family')))
#            remove(join(getcwd(),"2_"+x+'.family'))

    def testFamilyWriteToDB(self):
        pass

    def testFamilyWriteToDir(self):
        from os.path import isfile, join
        from os import getcwd, remove
        self.family1.add_child(self.family2)
        self.family1.add_child(self.family3)
        self.family1.add_child(self.family4)
        self.family2.add_child(self.family5)
        self.family2.add_child(self.family6)
        self.family3.add_child(self.family7)
        self.family3.add_child(self.family8)
        self.family4.add_child(self.family9)
        self.family4.add_child(self.family10)
        self.family1.write_to_dir()
        self.filenames = [x.get_uuid() for x in self.families]
        # This should be made recursive in the future.
        # The test struct is only 2 deep
        for x in [self.filenames[9]]:
            self.assertTrue(isfile(join(getcwd(), x+'.family')))
            remove(join(getcwd(), x+'.family'))
        for x in [self.filenames[8], self.filenames[7], self.filenames[6]]:
            self.assertTrue(isfile(join(getcwd(), x+'.family')))
            remove(join(getcwd(), x+'.family'))
        for x in [self.filenames[5], self.filenames[4], self.filenames[3],
                  self.filenames[2], self.filenames[1], self.filenames[0]]:
            self.assertTrue(isfile(join(getcwd(), x+'.family')))
            remove(join(getcwd(), x+'.family'))

    def testFamilyPoofFromDir(self):
        from os import remove, getcwd
        from os.path import join
        from copy import deepcopy

        self.family1.add_child(self.family2)
        self.family1.add_child(self.family3)
        self.family1.add_child(self.family4)
        self.family2.add_child(self.family5)
        self.family2.add_child(self.family6)
        self.family3.add_child(self.family7)
        self.family3.add_child(self.family8)
        self.family4.add_child(self.family9)
        self.family4.add_child(self.family10)

        self.family1_bak = deepcopy(self.family1)

        self.family1.write_to_dir()
        self.filenames = [x.get_uuid() for x in self.families]

        self.assertTrue(self.family1._get_flat())

        self.family1.poof_from_dir()

        self.assertEqual(self.family1, self.family1_bak)

        for x in self.families:
            remove(join(getcwd(), x.get_uuid()+'.family'))

    def testFamilyPoofFromDB(self):
        pass

if __name__ == '__main__':
    unittest.main()
