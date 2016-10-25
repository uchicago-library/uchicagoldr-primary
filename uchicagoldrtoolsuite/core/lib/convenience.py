from sys import stderr
from urllib.request import urlopen, URLError
from uuid import uuid1


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


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


def retrieve_resource_filepath(resource_path, pkg_name=None):
    """
    retrieves the filepath of some package resource, extracting it if need be

    __Args__

    1. resource_path (str): The path to the resource in the package

    __KWArgs__

    * pkg_name (str): The name of a package. Defaults to the project name

    __Returns__

    * (str): The filepath to the resource
    """
    from pkg_resources import Requirement, resource_filename
    if pkg_name is None:
        pkg_name = __name__.split('.')[0]
    return resource_filename(Requirement.parse(pkg_name), resource_path)


def retrieve_resource_string(resource_path, pkg_name=None):
    """
    retrieves the string contents of some package resource

    __Args__

    1. resource_path (str): The path to the resource in the package

    __KWArgs__

    * pkg_name (str): The name of a package. Defaults to the project name

    __Returns__

    * (str): the resource contents
    """
    from pkg_resources import Requirement, resource_string
    if pkg_name is None:
        pkg_name = __name__.split('.')[0]
    return resource_string(Requirement.parse(pkg_name), resource_path)


def retrieve_resource_stream(resource_path, pkg_name=None):
    """
    retrieves a stream of the contents of some package resource

    __Args__

    1. resource_path (str): The path to the resource in the package

    __KWArgs__

    * pkg_name (str): The name of a package. Defaults to the project name

    __Returns__

    * (io): an io stream
    """
    from pkg_resources import Requirement, resource_stream
    if pkg_name is None:
        pkg_name = __name__.split('.')[0]
    return resource_stream(Requirement.parse(pkg_name), resource_path)


def retrieve_controlled_vocabulary(vocab_name, built=True):
    """
    retrieves a controlled vocabulary from the package resources

    __Args__

    1. vocab_name (str): The name of some cv in controlledvocabs/ sans .json

    __KWArgs__

    * built (bool): Whether or not to build the FromJson object. Defaults
    to true. (This is not the same as building the cv itself)

    __Returns__

    * if built==True: An unbuilt controlled vocabulary
    * if built==False: An unbuilt ControlledVocabularyFromSource object
    """
    from controlledvocab.lib import ControlledVocabFromJson
    fname = retrieve_resource_filepath('controlledvocabs/'+vocab_name+'.json')
    cv = ControlledVocabFromJson(fname)
    if built:
        cv = cv.build()
    return cv
