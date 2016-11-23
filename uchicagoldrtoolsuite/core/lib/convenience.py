from sys import stderr
from codecs import encode
from urllib.request import urlopen, URLError
from uuid import uuid1, uuid4
from tempfile import TemporaryDirectory
from os.path import join
from os import scandir
from functools import wraps
from logging import getLogger


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


def recursive_scandir(path="."):
    for x in scandir(path):
        yield x
        if x.is_dir():
            yield from recursive_scandir(x.path)


class TemporaryFilePath:
    """
    Produces a file path that can be written to, closed, and then re-opened
    for reads on both Unix and Windows systems.

    Can be used as a context manager, eg:

    with TemporaryFilePath() as path:
        with open(path, 'wb') as dst:
            dst.write(b'123')
        with open(path, 'rb') as src:
            print(src.read())

    [out]: b'123'

    The file path will disappear when no more references to the object
    exist via the magic in the TemporaryDirectory() class. Anything written
    to it will be deleted. The same thing happens if it is used as a context
    manager - afterwards it disappears.
    """
    def __init__(self):
        # Throw this reference on the object, so it sticks around
        self.containing_dir = TemporaryDirectory()
        filename = uuid4().hex
        self.path = join(self.containing_dir.name, filename)

    def __fspath__(self):
        # Woo, 3.6 compatability
        return self.path

    def __enter__(self):
        return self.path

    def __exit__(self, *args):
        del self.containing_dir


def ldritem_to_premisrecord(item):
    from pypremis.lib import PremisRecord
    with TemporaryFilePath() as dst_path:
        with item.open() as src:
            with open(dst_path, 'wb') as dst:
                dst.write(src.read())
        r = PremisRecord(frompath=dst_path)
    return r


def is_presform_materialsuite(ms):
    try:
        p = ldritem_to_premisrecord(ms.premis)
        obj = p.get_object_list()[0]
        relations = obj.get_relationship()
        for relation in relations:
            if relation.get_relationshipType() == 'derivation' and \
                    relation.get_relationshipSubType() == 'has Source':
                return True
        return False
    except:
        return None


def hex_str_to_bytes(h):
    """
    Convert a hex string to bytes

    convert a utf-8 encoded string of characters assumed
    to be a series of bytes encoded as two characters
    (0-9, a-f) representing a base 16 (hexidecimal) number
    into a bytes object

    This function is the inverse of bytes_to_hex_str()

    __Args__

    1. h (str): The hex represented as a string

    __Returns__

    (bytes): The hex represented as a bytes object
    """
    return bytes(bytearray.fromhex(h))


def bytes_to_hex_str(b):
    """
    Convert a bytes object to a utf-8 encoded hexademical string representation

    converts a bytes object to a utf-8 encoded hexademical string.
    Each byte is encoded as a two character substring, and those
    substrings are concatenated together.

    This function is the inverse of hex_str_to_bytes()

    __Args__

    1. b (bytes): The bytes to be converted to a hex str

    __Returns__

    (str): The hexademical representation of the bytes
    """
    return encode(b, 'hex').decode('utf-8')


def hex_str_to_chr_str(h, encoding="utf-8"):
    """
    Tries to convert a utf-8 encoded hex byte representation
    to an encoded string of the characters at those code-points

    This conversion is attempted wholesale (aka, one bad byte breaks it).

    __Args__

    1. h (str): The utf-8 encoded hex representation of the bytes

    __KWArgs__

    encoding (str): The encoding of the hex byte representation

    __Returns__

    (str): A string of the characters represented by the hex
    """
    return hex_str_to_bytes(h).decode(encoding)


def hex_str_to_chr_array(h):
    # !!! WARNING !!!
    # This operation is potentially lossy, as there is no way
    # to reasonably escape where are writing an ordinal from
    # where we are writing a character with no advance knowledge
    # of the file names.
    #
    # One potential solution might be to prepend every file name with
    # a dynamically computed delimiter, but that makes the file names
    # fairly ugly, complicates the operation, and I don't know if there
    # is actually much demand for it. It also has an unhandled failure
    # case in instances where a file name contains every ASCII character,
    # which would have to be resolved by implementing multicharacter
    # delimiters, which starts to get really ugly really fast.
    """
    Return an array of ASCII characters and/or hex str byte representations
    for a given hex representation of some bytes.

    This function is paranoid, and opts to represent any characters outside
    of the ASCII range as a hexademical representation of the byte values
    at that point.

    __Args__

    h (str): Some bytes represented as a hexadecimal string

    __Returns__

    result([str]): An array of strings, for bytes representing a code point
        shared with ASCII this will be the resulting ASCII character, for those
        which fall outside of the ascii range it will be a hexademical
        representation of the byte value, prefixed with 0x.
    """
    if not len(h) % 2 == 0:
        raise ValueError("Improperly encoded hex string!")
    index = 2
    result = []
    while index <= len(h):
        byte_of_interest = h[index-2:index]
        ordinal = int(byte_of_interest, base=16)
        if ordinal >= int("80", base=16):
            character = hex(ordinal)
        else:
            character = chr(ordinal)
        result.append(character)
        index = index + 2
    return result


def iso8601_dt(dt=None, tz=None):
    """
    produce an iso8601 time string

    __KWArgs__

    * dt (datetime.datetime): The datetime object to produce a string for
    * tz (datetime.timezone): The timezone (if desired) to use in the str

    __Returns__

    * (str): The datetime/timezone formatted as an iso8601 string.
    """
    from datetime import datetime, timezone
    if tz is None:
        from datetime import timedelta
        # Central time
        tzd = timedelta(hours=-5)
        tz = timezone(tzd)
    if not isinstance(tz, timezone):
        raise ValueError('tz input needs to be a datetime.timezone')
    if dt is None:
        dt = datetime.now(tz)
    if not isinstance(dt, datetime):
        raise ValueError('dt input needs to be a datetime.datetime object')
    return dt.isoformat()


def sane_hash(hash_algo, flo, buf=65536):
    """
    compute a hash hexdigest without loading giant things into RAM

    __Args__

    1. hash_algo (str): an algo with an implementation hooked
        - md5
        - sha256
    2. flo (bytes io): a file like object to draw bytes from

    __KWArgs__

    * block_size (int): How many bytes to load into RAM at once

    __Returns__

    * (str): The hexdigest of the specified hashing algo on the file
    """
    from hashlib import md5, sha256
    from nothashes import crc32, adler32

    supported_algos = {
        'md5': md5,
        'sha256': sha256,
        'crc32': crc32,
        'adler32': adler32
    }

    hash_cls = supported_algos.get(hash_algo, None)

    if hash_cls is None:
        raise NotImplemented(
            'Unsupported hashing algo ({}) passed to sane_hash!'.format(hash_algo) +
            'Hashing algos supported are: '.format(str(supported_algos.keys()))
        )

    hasher = hash_cls()
    while True:
        try:
            data = flo.read(buf)
        except OSError as e:
            stderr.write("stream could not be read\n")
            stderr.write(e)
            stderr.write("\n")
        if not data:
            break
        hasher.update(data)
    return hasher.hexdigest()


def log_init_attempt(inst, log, _locals=None):

    def log_with_locals(inst, log, loc):
        if "self" in _locals:
            _locals['self'] = "omitted"
        log.debug(
            "Attempting init a new {} with locals {}".format(
                inst.__class__.__name__, str(_locals)
            )
        )

    def log_no_locals(inst, log):
        log.debug(
            "Attempting to init a new {}".format(
                inst.__class__.__name__
            )
        )

    if _locals is not None:
        try:
            log_with_locals(inst, log, _locals)
        except:
            # Most likely source of issues (I think) will be the locals not
            # being repr-able, so try without them in case of exceptions.
            # Justification here is that _some_ logging is better than none.
            # Emits a warning about using the fallback as well.
            log.warn(
                "Init attempt logging exception in {}, trying fallback.".format(
                    inst.__class__.__name__
                )
            )
            log_no_locals(inst, log)
    else:
        log_no_locals(inst, log)


def log_init_success(inst, log, log_repr=True):

    def _log_repr(inst, log):
        log.debug(
            "{} instance init'd successfully: {}".format(
                inst.__class__.__name__, inst.__repr__()
            )
        )

    def _no_log_repr(inst, log):
        log.debug(
            "{} instance init'd successfully".format(
                inst.__class__.__name__
            )
        )

    if log_repr:
        try:
            _log_repr(inst, log)
        except:
            # Most likely source of issues (I think) will be the class reprs
            # themselves in this case, so try without it in case of exceptions.
            # Justification here is that _some_ logging is better than none.
            # Emits a warning about using the fallback as well.
            log.warn(
                "Init success logging exception in {}, trying fallback.".format(
                    inst.__class__.__name__
                )
            )
            _no_log_repr(inst, log)
    else:
        _no_log_repr(inst, log)
