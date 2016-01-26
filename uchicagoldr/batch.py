
from collections import Iterable
from os import listdir, rmdir, mkdir, makedirs, walk
from os.path import join, isabs, isfile, isdir, relpath, abspath, exists, split
from types import GeneratorType
from urllib.request import urlopen
from re import match

from uchicagoldr.item import Item
from uchicagoldr.item import AccessionItem
from uchicagoldr.bash_cmd import BashCommand
from uchicagoldr.request import *
from uchicagoldr.error import LDRNonFatal, LDRFatal
from uchicagoldr.output import Output


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

    def _output_self_true(self):
        output = Output('batch', status=True)
        if not output.add_data(self):
            raise ValueError
        return output

    def _output_self_false(self, requests=[], errors=[]):
        output = Output('batch', status=False)
        for r in requests:
            output.add_request(r)
        for e in errors:
            output.add_error(e)
        if not output.add_data(self):
            raise ValueError
        return output

    def output(self):
        return self._output_self_true()

    def add_item(self, new_item):
        if not isinstance(new_item, Item):
            request = ProvideNewItemInstance()
            return self._output_self_false(requests=[request])
        try:
            self.items.append(new_item)
            return self._output_self_true()
        except Exception as e:
            error = LDRFatal(e)
            return self._output_self_false(errors=[error])

    def get_item_by_index(self, index):
        return self.get_items()[index]

    def get_item(self, item):
        return self.get_item_by_index(self.get_items().index(item))

    def output_item_by_index(self, index):
        if index > len(self.get_items()-1):
            return self._output_self_false(requests=[ProvideNewIndex()])
        try:
            output = Output(Item)
            if not output.add_data(self.get_item_by_index(index)):
                raise ValueError
            output.set_output_passed()
            return output
        except Exception as e:
            return self._output_self_false(errors=[LDRFatal(e)])

    def output_item(self, item):
        if not isinstance(item, Item):
            return self._output_self_false(requests=[ProvideNewItemInstance()])
        try:
            output = Output(Item)
            if not output.add_data(self.get_item):
                raise ValueError
            output.set_output_passed()
            return output
        except Exception as e:
            return self._output_self_false(errors=[LDRFatal(e)])

    def remove_item_by_index(self, index):
        try:
            self.get_items().pop(index)
            return self._output_self_true()
        except Exception as e:
            return self._output_self_false(errors=[LDRFatal(e)])

    def remove_item(self, item):
        try:
            self.get_items().pop(self.get_items().index(item))
            return self._output_self_true()
        except Exception as e:
            return self._output_self_false(errors=[LDRFatal(e)])

    def pop_item_by_index(self, index):
        return self.get_items().pop(index)

    def pop_item(self, item):
        return self.get_items().pop(self.get_items().index(item))

    def get_items(self):
        return self.items

    def output_items(self):
        output = Output('item')
        if not output.add_data(self.get_items()):
            raise ValueError
        output.set_output_passed()
        return output

    def set_items(self, items):
        if not (isinstance(items, GeneratorType) or
                isinstance(items, Iterable)):
            output = Output(None)
            output.add_request(ProvideNewItemsInstance())
            return output
        try:
            if isinstance(items, GeneratorType):
                self._set_items_gen(items)
                return self._output_self_true()
            elif isinstance(items, Iterable):
                self._set_items_iter(items)
                return self._output_self_true()
            else:
                e = LDRFatal(TypeError)
                return self._output_self_false(errors=[e])
        except Exception as e:
            return self._output_self_false(errors=[e])

    def _set_items_gen(self, generator_object):
        assert isinstance(generator_object, GeneratorType)
        self.items = generator_object

    def _set_items_iter(self, some_iterable):
        assert isinstance(some_iterable, Iterable)
        self.items = some_iterable


class Directory(Batch):
    def __init__(self,  directory_path, items=None):
        Batch.__init__(self, items=items)
        self.set_directory_path(directory_path)

    def __eq__(self, other):
        return Batch.__eq__(self, other) and \
            self.get_directory_path() == other.get_directory_path()

    def _output_self_true(self):
        output = Output('directory', status=True)
        if not output.add_data(self):
            raise ValueError
        return output

    def _output_self_false(self, requests=[], errors=[]):
        output = Output('directory', status=False)
        for r in requests:
            output.add_request(r)
        for e in errors:
            output.add_error(e)
        if not output.add_data(self):
            raise ValueError
        return output

        return self._output_self_true()

    def set_directory_path(self, a_path):
        if not isabs(a_path):
            r = ProvideAbsolutePath()
            return self._output_self_false(requests=[r])
        else:
            self.directory_path = abspath(a_path)
            return self._output_self_true()

    def get_directory_path(self):
        return self.directory_path

    def populate(self):
        errors = []
        for item in self._walk_directory_picking_files():
            s = self.add_item(item)
            if s.get_status() is not True:
                for request in s.get_requests():
                    errors.append(LDRFatal(NotImplemented))
                for error in s.get_errors():
                    errors.append(error)
        if len(errors) > 0:
            return self._output_self_false(errors=errors)
        else:
            return self._output_self_true()

    def add_item(self, new_item):
        if not isinstance(new_item, Item):
            return self._output_self_false(requests=[ProvideNewItemInstance()])
        if not (self.get_directory_path() in new_item.get_file_path()):
            e = LDRNonFatal("Item path did not contain " +
                            "directory path. Item not added.")
            return self._output_self_false(errors=[e])
        try:
            Batch.add_item(self, new_item)
            return self._output_self_true()
        except Exception as e:
            error = LDRFatal(e)
            return self._output_self_false(errors=[error])

    def clean_out_directory(self):
        """
        attempts to delete the batch directory; it will fail if
        the batch directory is not empty
        """
        try:
            rmdir(self.directory_path)
            return self._output_self_true()
        except Exception as e:
            return self._output_self_false(errors=[LDRFatal(e)])

    def _walk_directory_picking_files(self):
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


class StagingDirectory(Directory):
    def __init__(self, root, ark, ead, accno, items=None):
        self.root = root
        self.ark = ark
        self.ead = ead
        self.accno = accno
        self.data_path = join(root, ark, ead, accno, 'data')
        self.admin_path = join(root, ark, ead, accno, 'admin')
        self.exists_on_disk = False
        directory_path = join(root, ark)
        Directory.__init__(self, directory_path=directory_path, items=items)

    def _output_self_true(self):
        output = Output('stagingdirectory', status=True)
        if not output.add_data(self):
            raise ValueError
        return output

    def _output_self_false(self, requests=[], errors=[]):
        output = Output('stagingdirectory', status=False)
        for r in requests:
            output.add_request(r)
        for e in errors:
            output.add_error(e)
        if not output.add_data(self):
            raise ValueError
        return output

    def spawn(self):
        if self.validate().get_status() is True:
            e = LDRNonFatal('The staging directory already exists!')
            return self._output_self_false(errors=[e])

        try:
            if not isabs(self.root) or not exists(self.root):
                r = ProvideNewRoot()
                return self._output_self_false(requests=[r])
            exists_already = [x for x in walk(join(self.root, self.ark))]
            self.set_admin_path(join(self.root, self.ark,
                                     self.ead, self.accno, "admin"))
            self.set_data_path(join(self.root, self.ark,
                                    self.ead, self.accno, "data"))
            makedirs(self.get_admin_path(), mode=0o750)
            makedirs(self.get_data_path(), mode=0o750)
            open(join(self.get_admin_path(), 'record.json'), 'a').close()
            open(join(self.get_admin_path(),
                      'fileConversions.txt'), 'a').close()

            self.set_exists_on_disk(True)
            err = []
            if len(exists_already) > 0:
                for pre_existing_file in exists_already:
                    err.append(LDRNonFatal("A file already existed in the " +
                                           "specified staging directory: " +
                                           "{}".format(pre_existing_file)))
                return self._output_self_false(errors=err)
            else:
                return self._output_self_true()
        except Exception as e:
            return self.output_self_false(errors=[LDRFatal(e)])

    def get_data_path(self):
        return self.data_path

    def set_data_path(self, new_data_path):
        if not isabs(new_data_path):
            return self._output_self_false(requests=[ProvideNewDataPath()])
        self.data_path = new_data_path
        return self._output_self_true()

    def get_admin_path(self):
        return self.admin_path

    def set_admin_path(self, new_admin_path):
        if not isabs(new_admin_path):
            return self._output_self_false(requests=[ProvideNewAdminPath()])
        self.admin_path = new_admin_path
        return self._output_self_true()

    def get_exists_on_disk(self):
        return self.exists_on_disk

    def set_exists_on_disk(self, newBool):
        assert(isinstance(newBool, bool))
        if not isinstance(newBool, bool):
            return self._output_self_false(requests=InputType(bool))
        self.exists_on_disk = newBool

    def _check_dir(self, path, cardinality=None, reqDirs=[], reqFiles=[]):
        if not isabs(path):
            raise OSError
        result = True
        missing_dirs = []
        missing_files = []
        dir_contents = listdir(path)
        observed_cardinality = len(dir_contents)
        if cardinality is not None:
            if observed_cardinality != cardinality:
                result = False
        for d in reqDirs:
            if d in dir_contents and isdir(join(path, d)):
                pass
            else:
                missing_dirs.append(d)
                result = False
        for f in reqFiles:
            if f in dir_contents and isfile(join(path, f)):
                pass
            else:
                missing_files.append(f)
                result = False
        return (result, dir_contents, observed_cardinality,
                missing_dirs, missing_files)

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
            e = LDRNonFatal("The root directory path is not a directory " +
                            "on disk.\n" +
                            "Path: {}".format(path))
            return self._output_self_false(errors=[e])

        if split(path)[-1] == '':
            observedRoot = split(split(path)[0])[0]
        else:
            observedRoot = split(path)[0]

        if shouldBeRoot != observedRoot:
            e = LDRNonFatal("The observed root does not match the root " +
                            "specified in the object.\n" +
                            "Observed Root: {}".format(observedRoot) +
                            "Specified Root: {}".format(shouldBeRoot))
            return self._output_self_false(errors=[e])

        if split(path)[-1] == '':
            observedArk = split(split(path)[0])[1]
        else:
            observedArk = split(path)[1]

        if shouldBeArk != observedArk:
            e = LDRNonFatal("The observed ARK does not match the ARK " +
                            "specified in the object.\n" +
                            "Observed ARK: {}".format(observedArk) +
                            "Specified ARK: {}".format(shouldBeArk))
            return self._output_self_false(errors=[e])

        if not match("^\w{13}$", shouldBeArk):
            e = LDRNonFatal("The observed ARK does not contain " +
                            "13 characters.\n" +
                            "Observed ARK: {}".format(observedArk))
            return self._output_self_false(errors=[e])

        ArkDirCheck = self._check_dir(join(shouldBeRoot, shouldBeArk))
        if ArkDirCheck[2] != 1:
            e = LDRNonFatal("The ARK directory contains more than one " +
                            "folder.\n" +
                            "Path: {}\n".format(join(shouldBeRoot,
                                                     shouldBeArk)) +
                            "Contents: {}".format(str(ArkDirCheck[1])))
            return self._output_self_false(errors=[e])
        else:
            observedEAD = ArkDirCheck[1][0]

        if shouldBeEAD != observedEAD:
            e = LDRNonFatal("The observed EADID does not match the EADID " +
                            "specified in the object.\n" +
                            "Observed EADID: {}".format(observedEAD) +
                            "Specified EADID: {}".format(shouldBeEAD))
            return self._output_self_false(errors=[e])

        EADDirCheck = self._check_dir(join(shouldBeRoot, shouldBeArk,
                                           shouldBeEAD))
        if EADDirCheck[2] != 1:
            e = LDRNonFatal("The EAD directory contains more than one " +
                            "folder.\n" +
                            "Path: {}\n".format(join(shouldBeRoot,
                                                     shouldBeArk,
                                                     shouldBeEAD)) +
                            "Contents: {}".format(str(EADDirCheck[1])))
            return self._output_self_false(errors=[e])
        else:
            observedAccNo = EADDirCheck[1][0]

        if shouldBeAccNo != observedAccNo:
            e = LDRNonFatal("The observed accession number does not match " +
                            "the accession number specified in the object.\n" +
                            "Observed Acc No: {}".format(observedAccNo) +
                            "Specified Acc No: {}".format(shouldBeAccNo))
            return self._output_self_false(errors=[e])

        if not match("^\d{4}-\d{3}$", shouldBeAccNo):
            e = LDRNonFatal("The observed accession number does not " +
                            "contain four digits followed by a dash " +
                            "followed by three more digits.\n" +
                            "Observed Acc No: {}".format(observedAccNo))
            return self._output_self_false(errors=[e])

        AccNoDirCheck = self._check_dir(join(shouldBeRoot, shouldBeArk,
                                             shouldBeEAD, shouldBeAccNo),
                                        cardinality=2,
                                        reqDirs=['admin', 'data']
                                        )
        if AccNoDirCheck[0] is not True:
            e = LDRNonFatal("The observed accession number directory " +
                            "is not properly formatted. It should " +
                            "contain only two directories " +
                            "'admin' and 'data'.\n" +
                            "Path: {}\n".format(join(shouldBeRoot,
                                                     shouldBeArk,
                                                     shouldBeEAD,
                                                     shouldBeAccNo)) +
                            "Contents: {}".format(str(AccNoDirCheck[1])))
            return self._output_self_false(errors=[e])

        return self._output_self_true()

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
        if rootStatus.get_status() is not True:
            e = LDRNonFatal("Your staging root structure is not valid. " +
                            "The validator reports the following errors:\n" +
                            "\n".join(
                                [x.message for x in rootStatus.get_errors()]
                            ))
            return self._output_self_false(errors=[e])

        dataStatus = self._validate_organization(self.get_data_path())
        if not dataStatus[0]:
            e_str = ""
            if len(dataStatus['badPrefixes']) > 0:
                e_str.append("Malformed Prefixes: {}".format(", ".join(dataStatus['badPrefixes'])))
                e_str.append("\n")
            if len(dataStatus['missingDirs']) > 0:
                e_str.append("Missing Directories: {}".format(", ".join(dataStatus['missingDirs'])))
                e_str.append("\n")
            if len(dataStatus['missingReqs']) > 0:
                e_str.append("Missing Requirements: {}".format(", ".join(dataStatus['missingReqs'])))

            e = LDRNonFatal("Your data directory appears to be invalid.\n" +
                            e_str)
            return self._output_self_false(errors=[e])
        #
        adminStatus = self._validate_organization(
            self.get_admin_path(),
            reqTopFiles=['record.json',
                        'fileConversions.txt'],
            reqDirContents=['fixityFromOrigin.txt',
                            'fixityOnDisk.txt',
                            'log.txt',
                            'rsyncFromOrigin.txt'])

        if rootStatus.get_status() and dataStatus[0] and adminStatus[0]:
            dirs = [x for x in listdir(self.get_data_path())]
            for entry in dirs:
                assert(isdir(entry))
                data['containedDirs'].append(
                    self._validate_contained_folder(entry))
            for entry in data['containedDirs']:
                if entry[0] is not True:
                    return (False, data)

            return (True, data)

    def ingest(self, path, prefix=None, containingFolder=None,
               rehash=False, pattern=None):
        if not isdir(path):
            r = ProvideNewIngestTargetPath()
            return self._return_self_false(requests=[r])
        if prefix and containingFolder:
            e = LDRNonFatal("A prefix and a containing folder can not " +
                            "be specified at the same time. A prefix " +
                            "implies the creation of a new containing " +
                            "folder.")
            return self._return_self_false(errors=[e])
        if rehash and not containingFolder:
            e = LDRNonFatal("In order to read existing hashes you must "+
                            "specify a containing folder that already " +
                            "exists with hash data.")
            return self._return_self_false(errors=[e])

        if path[-1] != "/":
            e = LDRNonFatal("Path syntax is incorrect. " +
                            "Paths must end with a '/'")
            return self._return_self_false(errors=[e])
        if not self.validate().get_status():
            e = LDRNonFatal("Your staging directory is no longer valid. " +
                            "Remedy your staging directory on disk in " +
                            "order to continue ingesting new materials.")
        if not containingFolder:
            prefixDir = self._prefix_to_dir(prefix)
            workingData = join(self.get_data_path(), prefixDir)
            workingAdmin = join(self.get_admin_path(), prefixDir)
            mkdir(workingData)
            mkdir(workingAdmin)
        else:
            workingData = join(self.get_data_path(), containingFolder)
            workingAdmin = join(self.get_admin_path(), containingFolder)

        if not exists(workingData):
            e = LDRNonFatal("The containing folder for the data could " +
                            "not be found.")
            return self._return_self_false(errors=[e])
        if not exists(workingAdmin):
            e = LDRNonFatal("The containing folder for the admin files could " +
                            "not be found.")
            return self._return_self_false(errors=[e])

        self._move_files_into_staging(path, workingData, workingAdmin, pattern)
        self._hash_files_at_origin(path, workingAdmin, rehash, pattern)
        self._hash_files_in_staging(workingData, workingAdmin, rehash)
        add_new_items_output = self.populate()
        if not add_new_items_output.get_status():
            e = LDRNonFatal("A problem occured while attempting to " +
                            "repopulate the staging directory with an updated "
                            "listing. Errors reported follow:\n" +
                            "{}".format("\n".join(
                                [x.message for x in add_new_items_output.get_errors()])))

        return self._output_self_true()

    def _prefix_to_dir(self, prefix):
        existingPopSubDirs = [name for name in
                              self._getImmediateSubDirs(self.get_data_path())
                              if match('^'+prefix, name)]

        if len(existingPopSubDirs) == 0:
            return prefix+str(1)
        else:
            nums = [int(dirname.strip(prefix))
                    for dirname in existingPopSubDirs]
            nums.sort()
            nextNum = str(nums[-1]+1)
            return prefix+str(nextNum)

    def _getImmediateSubDirs(self, path):
        return [name for name in listdir(path) if isdir(join(path, name))]

    def _move_files_into_staging(self, path,
                                 workingData, workingAdmin, pattern):
        rsyncArgs = ['rsync', '-avz', path, workingData]
        rsyncCommand = BashCommand(rsyncArgs)
        assert(rsyncCommand.run_command()[0])
        with open(join(workingAdmin,
                       'rsyncFromOrigin.txt'), 'a') as f:
            f.write(str(rsyncCommand.get_data()[1])+'\n')
        # if isdir(path):
        #   thingsToMove = MovableItems()
        #   walker = FileWalker(path)
        #   for entry in walker:
        #       if match(pattern, entry):
        #           thingToMove = MovableItem(entry, path, workingData)
        #           thingsToMove.append(thingToMove)
        #   for thingToMove in thingsToMove:
        #       thingToMove.move()
        #       assert(thingToMove.moved)
        #       with open(join(workingAdmin,'mvLog.txt'),'a') as f:
        #           f.write(thingToMove.get_move_result())
        # elif isfile(path):
        #   thingToMove = MovableItem(path, split(path)[0], workingData)
        #   thingToMove.move()
        #   assert(thingToMove.moved)
        #   with open(join(workingAdmin,'mvLog.txt'),'a' as f:
        #       f.write(thingToMove.get_move_result())

    def _hash_files_at_origin(self, path, workingAdmin, rehash, pattern):
        if not rehash:
            if exists(join(workingAdmin, 'fixityFromOrigin.txt')):
                existingHashes = self._read_fixity_log(
                    join(workingAdmin, 'fixityFromOrigin.txt')
                )
            else:
                existingHashes = {}
        else:
            existingHashes = {}

        directory = Directory(path)
        directory.populate()
        if pattern is not None:
            for entry in directory.get_items():
                if not match(pattern, entry.get_file_path()):
                    directory.remove_item(entry)
        self._write_fixity_log(
            join(workingAdmin, 'fixityFromOrigin.txt'),
            directory,
            existingHashes
        )

    def _hash_files_in_staging(self, path, workingAdmin, rehash):
        if not rehash:
            if exists(join(workingAdmin, 'fixityOnDisk.txt')):
                existingHashes = self._read_fixity_log(
                    join(workingAdmin, 'fixityOnDisk.txt')
                )
            else:
                existingHashes = {}
        else:
            existingHashes = {}

        directory = Directory(path)
        directory.populate()
        self._write_fixity_log(
            join(workingAdmin, 'fixityOnDisk.txt'),
            directory,
            existingHashes)

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
        for item in directory.get_items():
            if item.test_readability():
                if existingHashes:
                    if relpath(
                        item.get_file_path(),
                        start=directory.get_directory_path()
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
        return Directory.add_item(self, new_item)

    def __eq__(self, other):
        return Directory.__eq__(self, other) and \
            self.get_root_path() == other.get_root_path() and \
            self.get_accession() == other.get_accession()

    def _output_self_true(self):
        output = Output('accessiondirectory', status=True)
        if not output.add_data(self):
            raise ValueError
        return output

    def _output_self_false(self, requests=[], errors=[]):
        output = Output('accessiondirectory', status=False)
        for r in requests:
            output.add_request(r)
        for e in errors:
            output.add_error(e)
        if not output.add_data(self):
            raise ValueError
        return output

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
        generator_of_items = self._walk_directory_picking_files(
                                                        self.directory_path
        )
        self.items = generator_of_items

    def _walk_directory_picking_files(self):
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
