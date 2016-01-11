
from collections import Iterable
from os import listdir, rmdir, mkdir
from os.path import join, isabs, isfile, isdir, relpath, abspath, exists, split
from types import GeneratorType
from urllib.request import urlopen
from re import match

from uchicagoldr.item import Item
from uchicagoldr.item import AccessionItem
from uchicagoldr.bash_cmd import BashCommand


class Batch(object):
    """
    This class holds a list of files as Item instances in a new accession
    """

    def __init__(self, items=None):
        self.items = []
        if isinstance(items, Iterable) or isinstance(items, GeneratorType) \
                or items is None:
            pass
        else:
            raise TypeError
        if items is not None:
            self.set_items(items)

    def __iter__(self):
        for item in self.get_items():
            yield item

    def __repr__(self):
        return str(self.get_items())

    def __eq__(self, other):
        eq = type(self) == type(other)
        if not eq:
            return False
        for item in self.get_items():
            eq = eq and item in other.get_items()
            if not eq:
                return False
        for item in other.get_items():
            eq = eq and item in self.get_items()
            if not eq:
                return False
        return eq

    def add_item(self, new_item):
        try:
            assert isinstance(new_item, Item)
            self.items.append(new_item)
            return (True, None)
        except Exception as e:
            return (False, e)

    def get_item_by_index(self, index):
        return self.get_items()[index]

    def get_item(self, item):
        return self.get_item_by_index(self.get_items().index(item))

    def remove_item_by_index(self, index):
        self.get_items().pop(index)

    def pop_item_by_index(self, index):
        return self.get_items().pop(index)

    def remove_item(self, item):
        self.get_items().pop(self.get_items().index(item))

    def pop_item(self, item):
        return self.get_items().pop(self.get_items().index(item))

    def set_items(self, items):
        assert(isinstance(items, GeneratorType) or isinstance(items, Iterable))
        if isinstance(items, GeneratorType):
            self.set_items_gen(items)
        if isinstance(items, Iterable):
            self.set_items_iter(items)

    def set_items_gen(self, generator_object):
        assert isinstance(generator_object, GeneratorType)
        self.items = generator_object

    def set_items_iter(self, some_iterable):
        assert isinstance(some_iterable, Iterable)
        self.items = some_iterable

    def get_items(self):
        return self.items


class Directory(Batch):
    def __init__(self,  directory_path, items=None):
        Batch.__init__(self, items=items)
        self.set_directory_path(directory_path)

    def __eq__(self, other):
        return Batch.__eq__(self, other) and \
            self.get_directory_path() == other.get_directory_path()

    def set_directory_path(self, a_path):
        if not isabs(a_path):
            raise ValueError("path is not absolute!")
        else:
            self.directory_path = abspath(a_path)

    def get_directory_path(self):
        return self.directory_path

    def walk_directory_picking_files(self):
        """
        walks a directory tree and creates a generator full of AccessionItem
        instances for each regular file
        """
        flat_list = listdir(self.get_directory_path())
        while flat_list:
            node = flat_list.pop()
            fullpath = join(self.get_directory_path(), node)
            if isfile(fullpath):
                i = Item(fullpath)
                yield i
            elif isdir(fullpath):
                for child in listdir(fullpath):
                    flat_list.append(join(fullpath, child))

    def populate(self):
        for item in self.walk_directory_picking_files():
            self.add_item(item)

    def add_item(self, new_item):
        assert isinstance(new_item, Item)
        assert(self.get_directory_path() in new_item.get_file_path())
        Batch.add_item(self, new_item)

    def clean_out_directory(self):
        """
        attempts to delete the batch directory; it will fail if
        the batch directory is not empty
        """
        rmdir(self.directory_path)


class StagingDirectory(Directory):
    def __init__(self, root, ark, ead, accno, items=None):
        self.root = root
        self.ark = ark
        self.ead = ead
        self.accno = accno
        self.data_path = join(root,ark,ead,accno,'data')
        self.admin_path = join(root,ark,ead,accno,'admin')
        self.exists_on_disk = False
        directory_path = join(root, ark)
        Directory.__init__(self, directory_path=directory_path, items=items)

    def spawn(self):
        if exists(join(self.root, self.ark)):
            return False

        try:
            assert(exists(self.root))
            mkAdminDirArgs = ['mkdir', '-p', join(self.root,
                                                  self.ark,
                                                  self.ead,
                                                  self.accno,
                                                  "admin")
                              ]
            mkAdminDirCommand = BashCommand(mkAdminDirArgs)
            assert(mkAdminDirCommand.run_command()[0])
            assert(mkAdminDirCommand.get_data()[1].returncode == 0)
            self.set_admin_path(join(self.root, self.ark,
                                     self.ead, self.accno, "admin"))

            topLevelReqFiles = ['fileConversions.txt',
                                'record.json',
                                ]
            for f in topLevelReqFiles:
                touchArgs = ['touch', join(self.get_admin_path(), f)]
                touchCommand = BashCommand(touchArgs)
                assert(touchCommand.run_command()[0])
                assert(touchCommand.get_data()[1].returncode == 0)

            mkDataDirArgs = ['mkdir', join(self.root,
                                           self.ark,
                                           self.ead,
                                           self.accno,
                                           "data")
                             ]
            mkDataDirCommand = BashCommand(mkDataDirArgs)
            assert(mkDataDirCommand.run_command()[0])
            assert(mkDataDirCommand.get_data()[1].returncode == 0)
            self.set_data_path(join(self.root, self.ark,
                                    self.ead, self.accno, "data"))

            self.set_exists_on_disk(True)
            return join(self.root, self.ark)
        except Exception as e:
            return e

    def get_data_path(self):
        return self.data_path

    def set_data_path(self, new_data_path):
        assert(isabs(new_data_path))
        self.data_path = new_data_path

    def get_admin_path(self):
        return self.admin_path

    def set_admin_path(self, new_admin_path):
        assert(isabs(new_admin_path))
        self.admin_path = new_admin_path

    def get_exists_on_disk(self):
        return self.exists_on_disk

    def set_exists_on_disk(self, newBool):
        assert(isinstance(newBool, bool))
        self.exists_on_disk = newBool

    def validate(self):
        path = self.directory_path
        shouldBeRoot = self.root
        shouldBeArk = self.ark
        shouldBeEAD = self.ead
        shouldBeAccNo = self.accno

        observedRoot = None
        observedArk = None
        observedEAD = None
        observedAccNo = None

        if not (isdir(path)):
            return (False, observedRoot, observedArk,
                    observedEAD, observedAccNo)

        if split(path)[-1] == '':
            observedRoot = split(split(path)[0])[0]
        else:
            observedRoot = split(path)[0]

        if shouldBeRoot is not None:
            if shouldBeRoot != observedRoot:
                return (False,
                        observedRoot, observedArk,
                        observedEAD, observedAccNo)
        shouldBeRoot = observedRoot

        if split(path)[-1] == '':
            observedArk = split(split(path)[0])[1]
        else:
            observedArk = split(path)[1]
        if shouldBeArk is not None:
            if shouldBeArk != observedArk:
                return (False,
                        observedRoot, observedArk,
                        observedEAD, observedAccNo)
        shouldBeArk = observedArk
        if not match("^\w{13}$", shouldBeArk):
            return (False,
                    observedRoot, observedArk,
                    observedEAD, observedAccNo)

        if len(listdir(join(shouldBeRoot, shouldBeArk))) == 1:
            observedEAD = listdir(join(observedRoot, shouldBeArk))[0]
        else:
            return (False,
                    observedRoot, observedArk,
                    observedEAD, observedAccNo)
        if shouldBeEAD is not None:
            if shouldBeEAD != observedEAD:
                return (False,
                        observedRoot, observedArk,
                        observedEAD, observedAccNo)
        shouldBeEAD = observedEAD

        if len(listdir(join(shouldBeRoot, shouldBeArk, shouldBeEAD))) == 1:
            observedAccNo = listdir(join(
                shouldBeRoot, shouldBeArk, shouldBeEAD))[0]
        else:
            return (False,
                    observedRoot, observedArk,
                    observedEAD, observedAccNo)
        if shouldBeAccNo is not None:
            if shouldBeAccNo != observedAccNo:
                return (False,
                        observedRoot, observedArk,
                        observedEAD, observedAccNo)
        shouldBeAccNo = observedAccNo
        if not match("^\d{4}-\d{3}$", shouldBeAccNo):
            return (False,
                    observedRoot, observedArk,
                    observedEAD, observedAccNo)

        for folder in ['admin', 'data']:
            if folder not in listdir(join(
                    shouldBeRoot, shouldBeArk, shouldBeEAD, shouldBeAccNo)):
                return (False,
                        observedRoot, observedArk,
                        observedEAD, observedAccNo)
        if len(listdir(join(
                shouldBeRoot, shouldBeArk, shouldBeEAD, shouldBeAccNo))) != 2:
            return (False,
                    observedRoot, observedArk,
                    observedEAD, observedAccNo)

        return (True,
                observedRoot, observedArk,
                observedEAD, observedAccNo)

    def _validate_organization(self, targetPath, reqTopFiles=[],
                               reqDirContents=[]):
        returnDict = {}
        returnDict['dirs'] = []
        returnDict['notDirs'] = []
        returnDict['prefixes'] = []
        returnDict['badPrefixes'] = []
        returnDict['missingDirs'] = []
        returnDict['missingReqs'] = []

        if not isdir(targetPath):
            return((False, returnDict))

        targetTopFileList = [x for x in
                             listdir(targetPath) if isfile(join(targetPath, x))]
        targetFolderList = [x for x in
                            listdir(targetPath) if isdir(join(targetPath, x))]

        for x in reqTopFiles:
            if x not in targetTopFileList:
                returnDict['missingReqs'].append(join(targetPath, x))
                return ((False, returnDict))

        for x in targetFolderList:
            returnDict['dirs'].append(x)

        if targetFolderList != listdir(targetPath):
            for x in listdir(targetPath):
                if x not in targetFolderList:
                    returnDict['notDirs'].append(x)

        for x in targetFolderList:
            prefix = match('^[a-zA-Z_\-]*', x)
            try:
                returnDict['badPrefixes'].append(prefix.group(1))
            except IndexError:
                returnDict['prefixes'].append(prefix.group(0))
            dirContents = [y for y in listdir(join(targetPath, x))]
            for req in reqDirContents:
                if req not in dirContents:
                    returnDict['missingReqs'].append(join(targetPath, x, req))

        returnDict['prefixes'] = set(returnDict['prefixes'])
        returnDict['badPrefixes'] = set(returnDict['badPrefixes'])

        for prefix in returnDict['prefixes']:
            prefixSet = [directory for directory in listdir(targetPath)
                        if match('^'+prefix, directory)]
            nums = []
            for folder in prefixSet:
                num = folder.lstrip(prefix)
                nums.append(int(num))
            maxNum = max(nums)
            for i in range(1, maxNum+1):
                if i not in nums:
                    returnDict['missingDirs'].append(prefix+str(num))
        if len(returnDict['missingDirs']) > 0:
            return((False, returnDict))
        if len(returnDict['badPrefixes']) > 0:
            return((False, returnDict))
        if len(returnDict['missingReqs']) > 0:
            return((False, returnDict))
        return (True, returnDict)

    def _read_fixity_log(self, path):
        assert(exists(path))
        existingFixity = {}
        try:
            with open(path, 'r') as f:
                for line in f.readlines():
                    splitLine = line.split('\t')
                    splitLine[-1] = splitLine[-1].rstrip('\n')
                    go = True
                    for entry in splitLine[1:]:
                        if entry == 'ERROR':
                            go = False
                    if not go:
                        continue
                    try:
                        existingFixity[splitLine[0]] = [splitLine[1], splitLine[2]]
                    except IndexError:
                        pass
        except:
            pass
        return existingFixity

    def _validate_contained_folder(self, containing_folder):
        destinationAdminRoot = self.get_admin_path()
        destinationAdminFolder = join(destinationAdminRoot, containing_folder)
        destinationDataRoot = self.get_data_path()
        destinationDataFolder = join(destinationDataRoot, containing_folder)

        existingOriginalFileHashes = self._read_fixity_log(
                                         join(
                                           destinationAdminFolder,
                                           'fixityFromOrigin.txt'
                                         )
                                     )
        existingMovedFileHashes = self._read_fixity_log(
                                     join(
                                       destinationAdminFolder,
                                       'fixityOnDisk.txt'
                                     )
                                  )

        notMoved = [key for key in existingOriginalFileHashes
                    if key not in existingMovedFileHashes]
        foreignFiles = [key for key in existingMovedFileHashes
                        if key not in existingOriginalFileHashes]
        badHash = [key for key in existingOriginalFileHashes
                   if key not in notMoved and
                   existingOriginalFileHashes[key] !=
                   existingMovedFileHashes[key]]

        returnDict = {}
        returnDict['Original File Hashes'] = existingOriginalFileHashes
        returnDict['Moved File Hashes'] = existingMovedFileHashes
        returnDict['Not Moved'] = notMoved
        returnDict['Foreign Files'] = foreignFiles
        returnDict['Bad Hashes'] = badHash
        if len(notMoved) == 0 and \
                len(foreignFiles) == 0 and \
                len(badHash) == 0:
            return (True, returnDict)
        else:
            return (False, returnDict)

    def audit(self):
        data = {}
        data['rootStatus'] = []
        data['dataStatus'] = []
        data['adminStatus'] = []
        data['containedDirs'] = []
        rootStatus = self.validate()
        dataStatus = self._validate_organization(self.get_data_path())
        adminStatus = self._validate_organization(self.get_admin_path(),
                                                  reqTopFiles=['record.json',
                                                               'fileConversions.txt'],
                                                  reqDirContents=['fixityFromOrigin.txt',
                                                                  'fixityOnDisk.txt',
                                                                  'log.txt',
                                                                  'rsyncFromOrigin.txt'])
        data['rootStatus'] = rootStatus
        data['dataStatus'] = dataStatus
        data['adminStatus'] = adminStatus

        if rootStatus[0] and dataStatus[0] and adminStatus[0]:
            dirs = [x for x in listdir(self.get_data_path())]
            for entry in dirs:
                assert(isdir(entry))
                data['containedDirs'].append(
                    self._validate_contained_folder(entry))
            for entry in data['containedDirs']:
                if entry[0] is not True:
                    return (False, data)

            return (True, data)
        else:
            return (False, data)

    def ingest(self, path, prefix=None, containingFolder=None, rehash=False):
        assert(isdir(path))
        assert(prefix or containingFolder)
        assert(not (prefix and containingFolder))
        if rehash:
            assert(containingFolder)

        if path[-1] != "/":
            assert(False)
        assert(self.validate()[0])
        if not containingFolder:
            prefixDir = self._prefix_to_dir(prefix)
            workingData = join(self.get_data_path(), prefixDir)
            workingAdmin = join(self.get_admin_path(), prefixDir)
            mkdir(workingData)
            mkdir(workingAdmin)
        else:
            workingData = join(self.get_data_path(), containingFolder)
            workingAdmin = join(self.get_admin_path(), containingFolder)

        assert(exists(workingData))
        assert(exists(workingAdmin))

        self._move_files_into_staging(path, workingData, workingAdmin)
        self._hash_files_at_origin(path, workingAdmin, rehash)
        self._hash_files_in_staging(workingData, workingAdmin, rehash)

    def _prefix_to_dir(self, prefix):
        existingPopSubDirs = [name for name in self._getImmediateSubDirs(self.get_data_path())
                          if match('^'+prefix, name)]

        if len(existingPopSubDirs) == 0:
            return prefix+str(1)
        else:
            nums = [int(dirname.strip(prefix)) for dirname in existingPopSubDirs]
            nums.sort()
            nextNum = str(nums[-1]+1)
            return prefix+str(nextNum)

    def _getImmediateSubDirs(self, path):
        return [name for name in listdir(path) if isdir(join(path, name))]

    def _move_files_into_staging(self, path, workingData, workingAdmin):
        rsyncArgs = ['rsync', '-avz', path, workingData]
        rsyncCommand = BashCommand(rsyncArgs)
        assert(rsyncCommand.run_command()[0])
        with open(join(workingAdmin,
                       'rsyncFromOrigin.txt'), 'a') as f:
            f.write(str(rsyncCommand.get_data()[1])+'\n')

    def _hash_files_at_origin(self, path, workingAdmin, rehash):
        if not rehash:
            if exists(join(workingAdmin,'fixityFromOrigin.txt')):
                existingHashes = self._read_fixity_log(join(workingAdmin,'fixityFromOrigin.txt'))
            else:
                existingHashes = {}
        else:
            existingHashes = {}

        directory = Directory(path)
        self._write_fixity_log(join(workingAdmin,'fixityFromOrigin.txt'), directory, existingHashes)

    def _hash_files_in_staging(self, path, workingAdmin, rehash):
        if not rehash:
            if exists(join(workingAdmin,'fixityOnDisk.txt')):
                existingHashes = self._read_fixity_log(join(workingAdmin,'fixityOnDisk.txt'))
            else:
                existingHashes = {}
        else:
            existingHashes = {}

        directory = Directory(path)
        self._write_fixity_log(join(workingAdmin,'fixityOnDisk.txt'), directory, existingHashes)

    def _read_fixity_log(self, path):
        existingFixity = {}
        with open(path, 'r') as f:
            for line in f.readlines():
                splitLine = line.split('\t')
                splitLine[-1] = splitLine[-1].rstrip('\n')
                go = True
                for entry in splitLine[1:]:
                    if entry == 'ERROR':
                        go = False
                if not go:
                    continue
                try:
                    existingFixity[splitLine[0]] = [splitLine[1], splitLine[2]]
                except IndexError:
                    pass
        return existingFixity

    def _write_fixity_log(self, path, directory, existingHashes=None):
        newHashes = {}
        directory.populate()
        for item in directory.get_items():
            if item.test_readability():
                if existingHashes:
                    if relpath(
                            item.get_file_path(), start=directory.get_directory_path()
                    ) in existingHashes:
                        continue
                item.set_sha256(item.find_sha256_hash())
                item.set_md5(item.find_md5_hash())
                newHashes[relpath(
                    item.get_file_path(), start=directory.get_directory_path()
                        )] = [item.get_sha256(), item.get_md5()]
        with open(path, 'a') as f:
            for entry in newHashes:
                f.write(entry+'\t'+newHashes[entry][0] +
                        "\t"+newHashes[entry][1]+'\n')


class AccessionDirectory(Directory):
    def __init__(self, directory_path, root, accession=None, items=None):
        Directory.__init__(self, directory_path=directory_path, items=items)
        self.set_root_path(root)
        self.accession = accession
        if self.get_accession() is None:
            self.set_accession(
                self.find_accession_from_relative_path()
            )

    def add_item(self, new_item):
        assert isinstance(new_item, AccessionItem)
        Directory.add_item(self, new_item)

    def __eq__(self, other):
        return Directory.__eq__(self, other) and \
            self.get_root_path() == other.get_root_path() and \
            self.get_accession() == other.get_accession()

    def get_accession(self):
        return self.accession

    def set_accession(self, new_accession):
        self.accession = new_accession

    def get_root_path(self):
        return self.root

    def mint_accession_identifier(self):
        url_data = urlopen("https://y1.lib.uchicago.edu/cgi-bin/minter/" +
                           "noid?action=minter&n=1")
        if url_data.status == 200:
            url_data = url_data.read()
        else:
            raise ValueError("Could not fetch batch identifier from " +
                             "RESTful NOID minter")
        return url_data.split('61001/').rstrip()

    def convert_to_relative_path(self, a_path=None):
        if not self.root:
            raise ValueError("There is no directory root on this batch!")
        else:
            if a_path is None:
                a_path = self.get_directory_path()
            directory_relative_to_root = relpath(a_path,
                                                 self.get_root_path())
        return directory_relative_to_root

    def set_root_path(self, a_path):
        if not isabs(a_path):
            raise ValueError("The path you entered is not absolute!")
        else:
            self.root = abspath(a_path)
        return True

    def find_accession_from_relative_path(self, a_path=None):
        if a_path is None:
            a_path = self.convert_to_relative_path(
                self.get_directory_path()
            )
        if isabs(a_path):
            raise ValueError("cannot get accession from an absolute path")
        else:
            accession, *tail = a_path.split('/')
            return accession

    def collect_from_directory(self, directory_path, root):
        assert isinstance(directory_path, str)
        assert(len(self.get_items() == 0))
        self.set_directory_path(directory_path)
        self.set_root_path(root)
        directory_relative_to_root = self. \
                                     convert_to_relative_path(directory_path)
        self.get_accession_from_relative_path(directory_relative_to_root)
        generator_of_items = self.walk_directory_picking_files(
                                                        self.directory_path
        )
        self.items = generator_of_items

    def walk_directory_picking_files(self):
        """
        walks a directory tree and creates a generator full of AccessionItem
        instances for each regular file
        """
        flat_list = listdir(self.get_directory_path())
        while flat_list:
            node = flat_list.pop()
            fullpath = join(self.get_directory_path(), node)
            if isfile(fullpath):
                i = AccessionItem(fullpath, self.get_root_path())
                yield i
            elif isdir(fullpath):
                for child in listdir(fullpath):
                    flat_list.append(join(fullpath, child))
