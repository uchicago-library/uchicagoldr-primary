class FileProcessor(object):
    """
    == attributes ==
    1. filewalker is an instance of FileWalker
    2. tree is an instance of FileWalker tree

    == Args ==
    1. directory is the directory that needs to be walked and all the file contents
    retrieved.
    2. source_root is a string representing the base of the origin file path that should
    not be copied to the destination.

    == KWArgs ==
    1. irrelevant part is an optional argument to init a FileProcessor that will start a
    tree with the substring of a string after the value of this kwarg.

    """
    def __init__(self, directory, source_root, irrelevant_part = None):
        """
        This initializes the FileProcessor with a call to the FileWalker that passes the
        directory and creates a generator of a walk of the directory structure. A
        FileWalkTree also gets created and the tree is populated with the directory
        structure of the filewalker contents with files at the leaves.
        """
        self.filewalker = FileWalker(directory)
        self.tree = FileWalkTree()

        for n in self.filewalker:
            self.tree.add_node(n, irrelevant_parts = irrelevant_part)

    def find_all_files(self):
        """
        This function returns a list of all leaves in the filewalktree.
        """
        return self.get_tree().get_files()

    def find_directories_in_a_directory(self, a_node):
        """
        == Parameter ==
        1. a_node : a treelib.Node object

        This function takes a treelib.Node object, locates that node in the tree and
        returns all branches of that node that are not leaves.
        """
        current_level = a_node
        subdirectories = [self.find_matching_node(x) for x in current_level.fpointer if not self.find_matching_node(x).is_leaf()]
        return subdirectories

    def pattern_matching_files_regex(self, regex):
        """
        == Args ==

        1. regex : a string representing a valid regular expression

        This function finds all leaves in the tree that have a tag that matches the regular
        expression entered.
        """
        matches = [x for x in self.get_tree().get_all_nodes() if \
                   re_compile(regex).search(x.tag) and x.is_leaf()]
        return matches

    def string_searching_files(self, val_string):
        """
        == Args ==

        1. val_string : a literal string

        This function finds all leaves in the tree that contain the literal string in the
        tag name.
        """
        matches =  [x for x in self.get_tree().get_files() if
                    self.get_tree().find_string_in_a_node_tag(x, val_string)]
        return matches

    def string_searching_subdirectories(self, val_string):
        """
        == Parameters ==

        1. val_string: a literal string

        This function finds all nodes that are not leaves with the literal string in the
        tag name.
        """
        matches = [x for x in self.get_tree().get_all_nodes() if
                   self.get_tree().is_it_a_subdirectory(x)]

        matches = [x for x in matches if self.get_tree(). \
                   find_string_in_a_node_tag(x, val_string)]
        return matches

    def find_subdirectory_at_particular_level_down(self, val_string, level):
        """
        == Args ==
        1. val_string : a literal string
        2. level : integer

        This function finds all nodse that are not leaves matching a literal string at a
        particular depth level entered.
        """
        level = int(level)
        potential_matches = self.string_searching_subdirectories(val_string)
        actual_matches = [x for x in potential_matches if self.get_tree().find_depth_of_a_node(x) == level]
        return actual_matches

    def find_matching_node(self, val_string):
        """
        == Parameters ==
        1. val_string : literal string

        This function returns either a single node that matches a specific identifier or
        False if there are no nodes with that identifier or a ValueError if the
        programmer has returned multiple tress with the same identifier.
        """
        matches = [x for x in self.get_tree().get_all_nodes() if self.get_tree().does_node_match_string(x, val_string)]
        if len(matches) > 1:
            raise ValueError("too many matches for that identifier")
        elif len(matches) == 0:
            return False
        return matches[0]

    def get_checksum(self, filepath):
        """
        == Parameters ==
        1. filepath : a string representing the absolute path to a file on-disk.

        This function takes a file path and returns an md5 checksum for that file.
        """
        blocksize = 65536
        md5_hash = md5()
        file_run = open(filepath, 'rb')
        buf = file_run.read(blocksize)
        while len(buf) > 0:
            md5_hash.update(buf)
            buf = file_run.read(blocksize)
        file_run.close()
        return md5_hash.hexdigest()

    def find_file_in_a_subdirectory(self, a_node, file_name_string):
        """
        == Args ==
        1. a_node : a treelib.Node object
        2. file_name_string : a literal string

        This function returns True/False whether a leaf with the literal string in the
        node identifier is below the node entered.
        """
        node = self.find_matching_node(a_node.identifier)
        if len([x for x in node.fpointer if file_name_string in x]) == 1:
            return True
        return False

    def find_files_in_a_subdirectory(a_node_name):
        return [x for x in self.find_matching_node(a_node_name).fpointer if x.is_leaf()]

    def get_tree(self):
        """
        This function returns the value of the tree attribute.
        """
        return self.tree

    def validate(self):
        """
        This method is left not implemented on FileProcessor. It must be defined for all
        subclasses.
        """
        return NotImplemented

    def validate_files(self):
        """
        This method is left not implemented on FileProcessor. It must be defined for all
        subclasses.
        """
        return NotImplemented

    def explain_validation_result(self):
        """
        This method is left not implemented on FileProcessor. It must be defined for all
        subclasses.
        """
        return NotImplemented
