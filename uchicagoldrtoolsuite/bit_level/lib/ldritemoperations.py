from urllib.request import urlopen, URLError
from uuid import uuid1
from hashlib import md5, sha256

from .abc.ldritem import LDRItem


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


def pairtree_a_string(input_to_pairtree):
    """
    returns a list of pairtree parts

    __Args__

    1. input_to_pairtree (str): a string that needs to be converted
    into pairtree parts
    """
    if len(input_to_pairtree) % 2 > 0:
        output = input_to_pairtree+'1'
    else:
        output = input_to_pairtree
    output = [output[i:i+2] for i in range(0, len(output), 2)]
    return output


def get_archivable_identifier(noid=False):
    """
    returns an archive-worthy identifier for a submission into the ldritem

    __KWArgs__

    1. test (bool): a flag that is defaulted to False that determines
    whether the output id string will be a noid. If the flag is False,
    it will return a uuid hex string. If it is False, it will return a
    CDL noid identifier.
    """

    if not noid:
        data_output = uuid1()
        data_output = data_output.hex
    else:
        request = urlopen("https://y1.lib.uchicago.edu/" +
                          "cgi-bin/minter/noid?action=mint&n=1")
        if request.status == 200:
            data = request.readlines()
            data_output = data.decode('utf-8').split('61001/')[1].rstrip()
        else:
            raise URLError("Cannot read noid minter located at" +
                           "https://y1.lib.uchicago.edu/cgi-bin/minter/" +
                           "noid?action=mint&n=1")
    return data_output


def move(origin_loc, destination_loc):
    """
    a variation on copy which rather than merely copy the byte-stream of
    the origin into the destination and deletes the origin

    __Args__

    1. origin_loc (LDRItem): origin_loc is the source data to move
    2. destination_loc (LDRItem): destination_loc is where the source
    should be moved
    """
    copy(origin_loc, destination_loc)
    origin_loc.delete(final=True)
    if not origin_loc.exists() and destination_loc.exists():
        return True
    else:
        return False


def copy(origin_loc, destination_loc, clobber):
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
    if not isinstance(origin_loc, LDRItem) or not \
            isinstance(destination_loc, LDRItem):
        raise TypeError("must pass two instances of LDRPathRegularFile" +
                        " to the copy function.")
    if clobber is False:
        if destination_loc.exists():
            return (True, False, "already present", None)

    origin_hash = md5()
    destination_hash = md5()
    origin_checksum = None
    destination_checksum = None

    with origin_loc.open('rb') as reading_file:
        with destination_loc.open('wb') as writing_file:
            while True:
                buf = reading_file.read(1024)
                if buf:
                    origin_hash.update(buf)
                    writing_file.write(buf)
                else:
                    origin_checksum = str(origin_hash.hexdigest())
                    break
    if destination_loc.exists():
        with destination_loc.open('rb') as dst:
            while True:
                buf = dst.read(1024)
                if buf:
                    destination_hash.update(buf)
                else:
                    destination_checksum = str(destination_hash.hexdigest())
                    break
        if destination_checksum == origin_checksum:
            return (True, True, "copied", destination_checksum)
        else:
            return (True, False, "copied", None)
    else:
        return (False, False, "not copied", None)

def hash_ldritem(ldritem, algo="md5", buffering=1024):

    supported_hashes = [
        "md5",
        "sha256"
    ]

    if algo not in supported_hashes:
        raise ValueError("{} is not a supported hash.".format(str(algo)) +
                         "Supported Hashes include:\n"
                         "{}".format(", ".join(supported_hashes)))

    if algo == "md5":
        hasher = md5()
    elif algo == "sha256":
        hasher = sha256()
    else:
        raise AssertionError("Implementation goofs in the LDR Item hasher.")

    hash_str = None

    with ldritem.open() as f:
        data = f.read(buffering)
        while data:
            hasher.update(data)
            data = f.read(buffering)
        hash_hex = hasher.hexdigest()
        hash_str = str(hash_hex)

    return hash_str

def duplicate_ldritem(src, dst, dst_mode="wb", buffering=1024, confirm=True):
    if not isinstance(src, LDRItem) or not isinstance(dst, LDRItem):
        raise ValueError("src and dst must be LDRItems")

    confirmation = None

    if confirm:
        write_hasher = md5()

    with src.open('rb') as src_flo:
        with dst.open(dst_mode) as dst_flo:
            data = src_flo.read(buffering)
            while data:
                if confirm:
                    write_hasher.update(data)
                dst_flo.write(data)

    if confirm:
        if str(write_hasher.hexdigest()) == hash_ldritem(dst):
            confirmation = True

    return confirmation


def copy2(src, dst, clobber=False, detection="hash", max_retries=3,
          buffering=1024, confirm=True):

    supported_detections = [
        "hash",
        "name"
    ]

    if detection not in supported_detections:
        raise ValueError("{} is not a supported clobber " +
                         "detection scheme.".format(str(detection)))

    if dst.exists():
        if not clobber:
            return None
        else: # Clobber stuff
            if detection is "hash":
                if hash_ldritem(src) == hash_ldritem(dst): # Its got the same hash, don't copy anything its already the same
                    return True
            elif detection is "name":
                if src.item_name == dst.item_name: # Its got the same name, don't copy anything its already the same
                    return True
            else: # Some mismatch between these impl ifs and the array at the top
                raise AssertionError("ldr item copy func error")

            while max_retries > -1:
                max_retries = max_retires - 1
                if not confirm: # Fly by the seat of our pants, don't check anything just copy the bytes
                    duplicate_ldritem(src, dst, buffering=buffering, confirm=False)
                    return True
                else:
                    if duplicateldritem(src, dst, buffering=buffering, confirm=True) is True:
                        return True
    else: # The dst doesn't exist
        while max_retries > -1:
            max_retries = max_retires - 1
            if not confirm: # Fly by the seat of our pants, don't check anything just copy the bytes
                duplicate_ldritem(src, dst, buffering=buffering, confirm=False)
                return True
            else:
                if duplicateldritem(src, dst, buffering=buffering, confirm=True) is True:
                    return True
    return False

