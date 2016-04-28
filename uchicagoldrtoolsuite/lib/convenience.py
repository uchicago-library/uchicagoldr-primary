from sys import stderr
from .structuring.ldrpathregularfile import LDRPathRegularFile


def sane_hash(hash_algo, file_path, block_size=65536):
    """
    compute a hash hexdigest without loading giant things into RAM

    __Args__

    1. hash_algo (str): an algo with an implementation hooked
        - md5
        - sha256
    2. file_path (str): the abspath to the file

    __KWArgs__

    * block_size (int): How many bytes to load into RAM at once

    __Returns__

    * (str): The hexdigest of the specified hashing algo on the file
    """
    from hashlib import md5, sha256
    if hash_algo == 'md5':
        hasher = md5
    elif hash_algo == 'sha256':
        hasher = sha256
    else:
        raise NotImplemented('Hashing algos supported are md5 and sha256')

    hash_result = hasher()
    with open(file_path, 'rb') as f:
        while True:
            try:
                data = f.read(block_size)
            except OSError as e:
                stderr.write("{} could not be read\n".format(file_path))
                stderr.write(e)
                Stderr.write("\n")
            if not data:
                break
            hash_result.update(data)
    return str(hash_result.hexdigest())


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
        pkg_name = 'uchicagoldr'
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
        pkg_name = 'uchicagoldr'
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
        pkg_name = 'uchicagoldr'
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


def copy(origin_loc, destination_loc):
    """
    __Args__

    1. origin_loc (LDRPathRegular): the file object that is the source that
    needs to be copied
    2. detination_loc (LDRPathRegularFile): the file object that is the
    destiatination for the source that needs to be copied

    __Returns__

    * if copy occurs: a tuple containing truth and an md5 hash string of the
      new file
    * if copy does not occur: a tuple containing false and the Nonetype
    """
    if not isinstance(origin_loc, LDRPathRegularFile)\
       and not isinstance(destination_loc, LDRPathRegularFile):
        raise ValueError("must pass two instances of LDRPathRegularFile" +
                         " to the copy function.")
    with origin_loc.open('rb') as reading_file:
        with destination_loc.open('wb') as writing_file:
            while True:
                buf = reading_file.read(1024)
                if buf:
                    writing_file.write(buf)
                else:
                    break
    if destination_loc.exists():
        destination_checksum = sane_hash('md5', destination_loc.item_name)
        destination_checksum_sha256 = sane_hash('sha256',
                                                destination_loc.item_name)
        origin_checksum = sane_hash('md5', origin_loc.item_name)
        if destination_checksum == origin_checksum:
            return (True, sane_hash('md5', destination_loc.item_name,
                                    destination_checksum_sha256))
    else:
        return (False, None, None)
