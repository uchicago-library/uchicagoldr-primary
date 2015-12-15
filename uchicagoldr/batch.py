
from collections import Iterable
from os import listdir, rmdir
from os.path import exists, join, isabs, isfile, isdir, relpath
from sqlalchemy.orm.query import Query
from types import GeneratorType
from urllib.request import urlopen

from uchicagoldr.item import Item


class Batch(object):
    """
    This class holds a list of files as Item instances in a new accession
    """

    items = []
    directory_path = ""
    root = ""
    identifier = ""

    def __init__(self, root,
                 directory=None,
                 query=None):
        assert exists(root)
        if query:
            assert isinstance(query, Query)
            self.query = query
        elif directory:
            assert exists(directory)
            self.directory_path = directory
        self.root = root
        self.items = []

    def __iter__(self):
        for item in self.get_items():
            yield item

    def add_item(self,new_item):
        try:
            assert isinstance(new_item, Item)
            self.items.append(new_item)
            return (True, None)
        except Exception as e:
            return (False, e)

    def find_batch_identifier(self):
        url_data = urlopen("https://y1.lib.uchicago.edu/cgi-bin/minter/" +
                           "noid?action=minter&n=1")
        if url_data.status == 200:
            url_data = url_data.read()
        else:
            raise ValueError("Could not fetch batch identifier from " +
                             "RESTful NOID minter")
        return url_data.split('61001/').rstrip()

    def find_items(self, from_db=False, from_directory=False):
        output = None
        if from_directory:
            if exists(self.directory_path):
                output = self.walk_directory_picking_files(self.directory_path)
        elif from_db:
            output = self.walk_database_query_picking_files()

        else:
            output = None
        return output

    def walk_directory_picking_files(self, directory):
        """
        walks a directory tree and creates a generator full of Item instances
        for each regular file
        """
        flat_list = listdir(self.directory_path)
        while flat_list:
            node = flat_list.pop()
            fullpath = join(directory, node)
            if isfile(fullpath):
                i = Item(fullpath, self.root)
                yield i
            elif isdir(fullpath):
                for child in listdir(fullpath):
                    flat_list.append(join(fullpath, child))

    def walk_database_query_picking_files(self):
        for n in self.query:
            item = Item(join(self.root, n.accession, n.filepath), self.root)
            if getattr(n, 'checksum', None):
                item.remote_hash = n.checksum
            if getattr(n, 'size', None):
                item.remote_size = n.size
            if getattr(n, 'mimetype', None):
                item.remote_mimetype = n.mimetype
            yield item

    def set_items(self, items):
        assert(isinstance(items, GeneratorType) or isinstance(items, Iterable))
        if isinstance(items, GeneratorType):
            set_items_gen(self, items)
        if isinstance(items, Iterable):
            set_items_iter(self, items)

    def set_items_gen(self, generator_object):
        assert isinstance(generator_object, GeneratorType)
        self.items = generator_object

    def get_items(self):
        return self.items

    def convert_to_relative_path(self, a_path):
        if not self.root:
            raise ValueError("There is no directory root on this batch!")
        else:
            directory_relative_to_root = relpath(self.directory_path,
                                                 self.root)
        return directory_relative_to_root

    def set_root_path(self, a_path):
        if not isabs(a_path):
            raise ValueError("The path you entered is not absolute!")
        else:
            self.root = a_path
        return True

    def define_path(self, a_path):
        if not exists(a_path):
            raise ValueError("path does not exist!")
        else:
            self.directory_path = a_path
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
        self.define_path(directory_path)
        self.set_root_path(root)
        directory_relative_to_root = self. \
                                     convert_to_relative_path(directory_path)
        self.get_accession_from_relative_path(directory_relative_to_root)
        generator_of_items = self.walk_directory_picking_files(
                                                        self.directory_path
        )
        self.items = generator_of_items

    def collect_from_database(self, database_object, queryable, query_object,
                              root):
        query = database_object.session.query(queryable).filter(query_object)
        if query.count() > 0:
            generator_of_items = self.walk_database_query_picking_files(
                                                                query,
                                                                root,
            )
            self.items = generator_of_items
        else:
            raise ValueError("Your database query did not have any results!")

    def set_items_iter(self, some_iterable):
        assert isinstance(some_iterable, Iterable)
        self.items = some_iterable

    def clean_out_batch(self):
        """
        attempts to delete the batch directory; it will fail if
        the batch directory is not empty
        """
        rmdir(self.directory)
