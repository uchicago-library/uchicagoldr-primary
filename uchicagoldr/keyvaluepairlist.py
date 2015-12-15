from collections.abc import MutableSequence

from uchicagoldr.keyvaluepair import KeyValuePair


class KeyValuePairList(MutableSequence):
    def __init__(self,init_list=[]):
        self.innerList = []
        for entry in init_list:
            if not isinstance(entry, KeyValuePair):
                raise TypeError
            else:
                self.innerList.append(entry)
        if not self._check_recursion():
            raise RecursionError


    def __iter__(self):
        for entry in self.innerList:
            yield entry

    def __getitem__(self, index):
        try:
            return self.innerList[index]
        except Exception as e:
            raise e

    def __setitem__(self, index, value):
        if not isinstance(value, KeyValuePair):
            raise ValueError

        try:
            self.innerList.insert(index, value)
        except Exception as e:
            raise e
        if not self._check_recursion():
            raise RecursionError

    def __delitem__(self, index):
        try:
            del self.innerList[index]
        except Exception as e:
            raise e

    def __len__(self):
        return len(self.innerList)

    def __repr__(self):
        return self.innerList.__repr__()

    def __str__(self):
        return str(self.innerList)

    def _check_recursion(self, seen=None):
        noInfin = True

        if seen is None:
            seen = []

        if self in seen:
            return False

        if len(self) == 0:
            return True

        seen.append(self)
        for entry in self:
            if isinstance(entry.get_value(), KeyValuePairList):
                noInfin = noInfin and entry.get_value()._check_recursion(seen=seen)
                if not noInfin:
                    break

        return noInfin

    def insert(self, index, value):
        if not isinstance(value, KeyValuePair):
            raise ValueError
        try:
            self.innerList.insert(index, value)
        except Exception as e:
            raise e
        if not self._check_recursion():
            raise RecursionError

    def append(self, value):
        if not isinstance(value, KeyValuePair):
            raise ValueError
        try:
            self.innerList.append(value)
        except Exception as e:
            raise e
        if not self._check_recursion():
            raise RecursionError

    def extend(self, values):
        for v in values:
            if not isinstance(v, KeyValuePair):
                raise ValueError
            self.innerList.append(v)
        if not self._check_recursion():
            raise RecursionError

    def keys(self):
        keyList = []
        for kvp in self.innerList:
            keyList.append(kvp.get_key())
        return keyList

    def values(self):
        valueList = []
        for kvp in self.innerList:
            valueList.append(kvp.get_value())
        return valueList
