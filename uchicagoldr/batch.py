
from collections import Iterable
from os import listdir, rmdir
from os.path import exists, join, isabs, isfile, isdir, relpath
from types import GeneratorType
from urllib.request import urlopen

from uchicagoldr.item import Item
from uchicagoldr.item import AccessionItem


class Batch(object):
    """
    This class holds a list of files as Item instances in a new accession
    """

    def __init__(self, items=[]):
        self.set_items(items)

    def __iter__(self):
        for item in self.get_items():
            yield item

    def __repr__(self):
        return str(self.get_items())

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

    def __init__(self,  directory_path, items=[]):
        Batch.__init__(self, items=items)
        self.set_directory_path(directory_path)

    def set_directory_path(self, a_path):
        if not isabs(a_path):
            raise ValueError("path is not absolute!")
        else:
            self.directory_path = a_path

    def get_directory_path(self):
        return self.directory_path

#    def walk_directory_picking_files(self, directory):
#        """
#        walks a directory tree and creates a generator full of Item instances
#        for each regular file
#        """
#        flat_list = listdir(self.directory_path)
#        while flat_list:
#            node = flat_list.pop()
#            fullpath = join(directory, node)
#            if isfile(fullpath):
#                i = Item(fullpath)
#                yield i
#            elif isdir(fullpath):
#                for child in listdir(fullpath):
#                    flat_list.append(join(fullpath, child))

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
                i = AccessionItem(fullpath)
                yield i
            elif isdir(fullpath):
                for child in listdir(fullpath):
                    flat_list.append(join(fullpath, child))

    def populate(self):
        for item in self.walk_directory_picking_files():
            self.add_item(item)

    def add_item(self, new_item):
        try:
            assert isinstance(new_item, Item)
            assert(self.get_directory_path() in new_item.get_file_path())
            self.items.append(new_item)
            return (True, None)
        except Exception as e:
            return (False, e)

    def clean_out_directory(self):
        """
        attempts to delete the batch directory; it will fail if
        the batch directory is not empty
        """
        rmdir(self.directory_path)


class AccessionDirectory(Directory):

    def __init__(self, directory_path, root, accession=None, items=[]):
        Directory.__init__(self, directory_path=directory_path, items=items)
        self.set_root_path(root)
        self.accession = accession
        if self.get_accession() is None:
            self.get_accession_from_relative_path(
                self.convert_to_relative_path(self.get_directory_path())
            )

    def add_item(self, new_item):
        try:
            assert isinstance(new_item, AccessionItem)
            self.items.append(new_item)
            return (True, None)
        except Exception as e:
            return (False, e)

    def get_accession(self):
        return self.accession

    def set_accession(self, new_accession):
        self.accession = new_accession

    def get_root(self):
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

    def convert_to_relative_path(self, a_path):
        if not self.root:
            raise ValueError("There is no directory root on this batch!")
        else:
            directory_relative_to_root = relpath(self.get_directory_path(), self.get_root())
        return directory_relative_to_root

    def set_root_path(self, a_path):
        if not isabs(a_path):
            raise ValueError("The path you entered is not absolute!")
        else:
            self.root = a_path
        return True

    def get_accession_from_relative_path(self, a_path):
        if isabs(a_path):
            raise ValueError("cannot get accession from an absolute path")
        else:
            accession, *tail = a_path.split('/')
            self.accession = accession
        return True

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
                i = AccessionItem(fullpath, self.get_root())
                yield i
            elif isdir(fullpath):
                for child in listdir(fullpath):
                    flat_list.append(join(fullpath, child))

    def populate(self):
        for item in self.walk_directory_picking_files():
            self.add_item(item)
