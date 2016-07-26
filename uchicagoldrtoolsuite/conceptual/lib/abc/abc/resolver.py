from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from json import dumps

from Crypto.Random import random
from Crypto.PublicKey import DSA
from Crypto.Hash import SHA

from uchicagoldrtoolsuite.core.lib.convenience import iso8601_dt

#class Resolver(metaclass=ABCMeta):
class Resolver:

    _key = None

    @abstractmethod
    def resolve(self, r):
        pass

    def write_key(self, f):
        # THIS FILE CONTAINS YOUR PRIVATE KEY
        if self.key is None:
            raise ValueError("No associated key!")
        f.write("\n".join((str(x) for x in self._key_to_tup)))

    @abstractmethod
    def read_key(self, f):
        d = f.read()
        splits = d.split("\n")
        tup = (splits[0], splits[1], splits[2], splits[3], splits[4])
        self.key = self._key_from_tup(tup)

    def sign_request(self, r):
        # See notes about k values and tradeoffs here:
        # https://www.dlitz.net/software/pycrypto/doc/
        h = SHA.new(r).digest()
        return self.key.sign(h,
                             random.StrongRandom().randint(1, self.pubkey.q-1))

    def generate_request(self, uuid, component, index=None):
        d = OrderedDict()
        d['uuid'] = uuid,
        d['component'] = component,
        d['index'] = index,
        d['timestamp'] = iso8601_dt()
        r = OrderedDict()
        r['data'] = d
        r['signature'] = self.sign_request(dumps(d))
        return dumps(r)

    def init_keys(self, bits=2048):
        self.key = DSA.generate(bits)

    def get_key(self):
        return self._key

    def set_key(self, key):
        if not isinstance(key, DSA._DSAobj):
            raise ValueError("Keys must be Crypto.PublicKey.DSA._DSAobj's!")
        if not key.can_sign():
            raise ValueError("Inappropriate key - Cannot sign.")
        self._key = key

    def del_key(self):
        self._key = None

    def get_pubkey(self):
        if self.key is None:
            raise ValueError("No associated key found!")
        return self.key.publickey()

    def _key_to_tup(self):
        if self.key is None:
            raise ValueError("No associated key found!")
        return (self.key.y, self.key.g, self.key.p, self.key.q, self.key.x)

    def _key_from_tup(self, tup):
        if not isinstance(tup, tuple):
            raise ValueError("Not a tuple")
        return DSA.construct(tup)

    key = property(get_key, set_key, del_key)
    pubkey = property(get_pubkey)
