class WalkTree(object):
    """
    == Attributes ===

    1. tree_root : treelib.Tree
    2. expanded_node_list : list containing 1 or more treelib.Node

    This
    """

    def __init__(self):
        self.tree_root = None
        self.expanded_node_list = None

    def add_node(self, value, sep="/"):
        value_parts = value.split(sep)[1:]
        if not self.tree_root:
            self.tree_root = Tree()
            self.tree_root.create_node(value_parts[0],join('/',value_parts[0]))
        parent = self.tree_root.root
        for position, value_part in enumerate(value_parts)[1:]:
            self.tree_root.create_node(value_part, join(parent, value_part), parent=parent)

    def remove_node(self, value):
        self.tree_root.remove_node(value)

    def get_all_nodes(self):
        self._expand_node_list()
        return self.expanded_node_list

    def _expand_node_list(self):
        if not self.expanded_node_list:
            self.expanded_node_list = self.tree_root.all_nodes()
        else:
            return False
        return True
