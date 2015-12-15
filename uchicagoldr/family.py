from pickle import dump, load
from os import getcwd
from os.path import exists, isdir, join, isfile
from uuid import uuid4

from uchicagoldr.filepointer import FilePointer
from uchicagoldr.keyvaluepair import KeyValuePair
from uchicagoldr.keyvaluepairlist import KeyValuePairList


def load_family_from_dir(uuid, dir):
    pass


def load_family_from_db(uuid):
    pass


class Family(object):

    # For pickling... #.#.# = incompat.not_a_good_idea.minor_upgrade
    version = "0.0.1"

    def __init__(self, children=None, descs=None):

        self.children = []
        self.descs = []
        self.uuid = ""
        self.flat = False

        if isinstance(children, list) or children is None:
            pass
        else:
            raise TypeError
        if isinstance(descs, KeyValuePairList) or descs is None:
            pass
        else:
            raise TypeError

        self.uuid = str(uuid4())

        if children is not None:
            for child in children:
                self.add_child(child)

        if descs is not None:
            for desc in descs:
                self.add_desc(desc)

    def __repr__(self):
        return "UUID: {}\nChildren: {}\nDescs: {}".format(self.uuid,
                                                          str(self.children),
                                                          str(self.descs)
                                                          )

    def __str__(self, _depth=0):
        strRep = "UUID: {}\n".format(self.uuid)
        strRep = strRep+"\t"*_depth+"Descs: "+str(len(self.get_descs()))
        for desc in self.get_descs():
            strRep = strRep+'\n'+'\t'*_depth+" "+desc.__str__()
        strRep = strRep+"\n"+"\t"*_depth+"Children: " + \
                                        str(len(self.get_children()))
        for child in self.get_children():
            strRep = strRep+'\n'+"\t"*(_depth+1)+child.__str__(_depth=_depth+1)
        if len(self.get_children()) == 0:
            strRep += '\n'
        return strRep

    def __eq__(self, other):
        eq = isinstance(other, Family)
        if eq is True:
            eq = eq and self.get_descs() == other.get_descs()
        if eq is True:
            eq = eq and self.get_children() == other.get_children()
        if eq is True:
            for i in range(len(self.get_children())):
                eq = eq and (self.get_children()[i] == other.get_children()[i])
        return eq

    def __iter__(self):
        for child in self.children:
            yield child

    def _key_conflict(self, new_key):
        for entry in self.descs:
            if entry.get_key() == new_key:
                return True
        return False

    def _uniq_child(self, new_child):
        if len(self.get_children() == 0):
            return True
        for child in self.children:
            if child == new_child:
                return False
            if isinstance(child, Family):
                return self._uniq_child(new_child)

    def _check_recursion(self, seen=None):
        if seen is None:
            seen = []

        if self in seen:
            return False

        if len(self.get_children()) == 0:
            return True

        allFilePointers = True
        for child in self.get_children():
            allFilePointers = allFilePointers and isinstance(child, FilePointer)

        if allFilePointers:
            return True

        seen.append(self)
        for child in self.get_children():
            if isinstance(child, Family):
                return child._check_recursion(seen=seen)

    def _set_flat(self, new_flat):
        assert(isinstance(new_flat, bool))
        self.flat = new_flat

    def _get_flat(self):
        return self.flat

    def _toggle_flat(self):
        if self._get_flat() == True:
            self._set_flat(False)
        else:
            self._set_flat(True)
        return self._get_flat()

    def check_not_flat(self):
        if self._get_flat() == True:
            raise RuntimeError
        return True

    def check_flat(self):
        if self._get_flat() == False:
            raise RuntimeError
        return True

    def get_uuid(self):
        return self.uuid

    def add_child(self, child, index=None):
        assert(self.check_not_flat())
        assert(isinstance(child, Family) or
               isinstance(child, FilePointer))
        for cur_child in self.get_children():
            if child is cur_child:
                raise ValueError

        if index is None:
            self.children.append(child)
        else:
            assert(isinstance(index, int))
            assert(index > -1 and index < len(self.children))
            self.children.insert(index, child)

        if isinstance(child, Family):
            if not self._check_recursion():
                raise RecursionError

    def remove_child_by_index(self, index):
        self.get_children().pop(index)

    def pop_child_by_index(self, index=None):
        if index is None:
            index=len(self.get_children())-1
        return self.get_children().pop(index)

    def remove_child(self, child):
        assert(self.check_not_flat())
        self.remove_child_by_index(self.get_children().index(child))

    def pop_child(self, child):
        assert(self.check_not_flat())
        return self.pop_child_by_index(self.get_children().index(child))

    def get_child(self, child):
        assert(self.check_not_flat())
        return self.get_children()[self.get_children().index(child)]

    def get_child_by_index(self, index):
        return self.get_children()[index]

    def set_children(self, new_children):
        assert(isinstance(new_children, list))
        self.children = []
        for entry in new_children:
            assert(
                isinstance(entry, Family) or
                isinstance(entry, FilePointer)
            )
            self.children.append(entry)
        assert(self._check_recursion())

    def get_children(self):
        return self.children

    def add_desc(self, keyValuePair, index=None):
        assert(isinstance(keyValuePair, KeyValuePair))
        assert(keyValuePair not in self.descs)
        assert(not self._key_conflict(keyValuePair.get_key()))
        if index is None:
            self.descs.append(keyValuePair)
        else:
            assert(isinstance(index, int))
            assert(index > -1 and index < len(self.descs))
            self.descs.insert(index, keyValuePair)

    def remove_desc_by_index(self, index_to_del):
        return self.get_descs().pop(index_to_del)

    def remove_desc_by_key(self, key_to_del):
        returns = []
        for desc in self.descs:
            if desc.get_key() == key_to_del:
                returns.append(self.descs.pop(self.descs.index(desc)))
        return returns

    def remove_desc_by_value(self, value_to_del):
        returns = []
        for desc in self.descs:
            if desc.get_value() == value_to_del:
                returns.append(self.descs.pop(self.descs.index(desc)))
        return returns

    def get_descs(self):
        return self.descs

    def get_desc_by_key(self, key):
        returns = []
        for desc in self.get_descs():
            if desc.get_key() == key:
                returns.append(desc)
        return returns

    def get_desc_by_value(self, value):
        returns = []
        for desc in self.get_descs():
            if desc.get_value() == value:
                returns.append(desc)
        return returns

    def get_desc_by_index(self, index):
        return self.get_descs()[index]

    def set_descs(self, new_descs):
        if not isinstance(new_descs, KeyValuePairList):
            raise TypeError
        for entry in new_descs:
            if not isinstance(entry, KeyValuePair):
                raise TypeError
        self.descs = new_descs

    def flatten(self, return_refs=False):
        assert(self.check_not_flat())
        flatChildArray = []
        if return_refs:
            refs = []
        for child in self.get_children():
            flatChildArray.append(child.get_uuid())
            if return_refs:
                refs.append(child)
        self.children = flatChildArray
        self._toggle_flat()
        if return_refs:
            return refs

    def poof_from_dir(self, path=getcwd()):
        assert(self.check_flat())

        if len(self.get_children()) > 0:
            poofed_children=[]
            for child in self.get_children():
                with open(child+'.family', 'rb') as f:
                    poofed_children.append(load(f))
            self.children = poofed_children
            for child in self.get_children():
                if isinstance(child, Family):
                    child.poof_from_dir(path=path)

    def poof_from_db(self):
        pass

    def write_to_dir(self, path=getcwd(), clobber=False):
        from os.path import isdir
        assert(self.check_not_flat())
        assert(isdir(path))

        leaf = False

        if not leaf and len(self.get_children()) == 0:
            leaf = True

        if not leaf and self._get_flat():
            leaf = True

        if not leaf:
            allChildrenFlat = True
            for child in self.get_children():
                flat = child._get_flat()
                allChildrenFlat = allChildrenFlat and flat
                if not flat:
                    break
            leaf = allChildrenFlat

        if leaf:
            if isinstance(self, Family):
                self.flatten()
            self.write_to_file(file_name=self.get_uuid()+'.family', path=path, clobber=clobber)

        else:
            for child in self.get_children():
                if isinstance(child, Family):
                    child.write_to_dir(path=path, clobber=clobber)
                elif isinstance(child, FilePointer):
                    child.write_to_file(path=path, clobber=clober)
            self.write_to_dir(path=path, clobber=clobber)

    def write_to_file(self, path=getcwd(), file_name=None, clobber=False):
        if file_name is None:
            file_name = self.get_uuid() + '.family'
        assert(isinstance(path, str))
        assert(isinstance(file_name, str))
        assert(isinstance(clobber, bool))
        assert(isdir(path))
        if clobber is False:
            assert(not exists(join(path, file_name)))
        with open(join(path, file_name), 'wb') as f:
            dump(self, f)

    def write_to_db(self):
        pass
