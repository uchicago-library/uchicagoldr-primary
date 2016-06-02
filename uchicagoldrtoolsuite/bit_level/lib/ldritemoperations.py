from hashlib import md5
from os.path import join, split
from tempfile import TemporaryFile
from urllib.request import urlopen, URLError
from uuid import uuid1
from hashlib import md5, sha256

from uchicagoldrtoolsuite.core.lib.idbuilder import IDBuilder
from .abc.ldritem import LDRItem

from .ldrpath import LDRPath

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


def read_metadata_from_file_object(attribute_string,
                                   parser_object, msuite=None, ldritem=None):
    """
    returns an instantiated parser object containing data read
    from a ldritem object
    """

    if msuite:
        a_file_object = getattr(msuite, attribute_string, None)
    elif ldritem:
        a_file_object = ldritem

    output = None
    if a_file_object is not None:
        pass
    else:
        raise ValueError(
            "a materialsuite is missing the attribute {}".
            format(attribute_string))
    with TemporaryFile() as tempfile:
        with a_file_object.open('rb') as read_file:
            while True:
                buf = read_file.read(1024)
                if buf:
                    tempfile.write(buf)
                else:
                    break
            tempfile.seek(0)
            try:
                if parser_object.__name__ == 'PremisRecord':
                    output = parser_object(frompath=tempfile)
                elif parser_object.__name__ == 'HierarhcicalRecord':
                    output = parser_object(fromfile=tempfile)
                else:
                    output = parser_object(tempfile)
            except Exception as e:
                raise e(
                    "something went wrong in read_metadata_from_file_object" +
                    "and couldn't create an instance of {}".format(
                        parser_object.__name___))
    return output


def get_an_agent_id(id_string, in_package=True):
    def get_premis_agents_file():
        if in_package:
            this_dir, this_filename = split(__file__)
            return join(this_dir, 'premis', 'agents.txt')
        else:
            return join("")

    def get_agent_data():
        agent_file = LDRPath(get_premis_agents_file())
        all_lines = []
        with agent_file.open('rb') as read_file:
            while True:
                buf = read_file.read(1024)
                if buf:
                    lines = buf.split(b"\n")
                    all_lines.extend(lines)
                else:
                    break
        return all_lines

    id_string = bytes(id_string.encode('utf-8'))
    data = get_agent_data()
    for n_line in data:
        if id_string in n_line:
            return n_line.split(b",")[0].decode("utf-8")
    new_id = IDBuilder().build("premisID").show()
    with LDRPath("/home/tdanstrom/premis/agents.txt").\
      open('ab') as writing_file:
        new_line_string = "\n{},{}".\
                          format(new_id[1], id_string.decode('utf-8'))
        new_line_string = new_line_string.encode('utf-8')
        writing_file.write(bytes(new_line_string))
    return new_id[1]


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


def hash_ldritem(ldritem, algo="md5", buffering=1024):
    """
    hash any flavor of LDRItem

    __Args__

    1. ldritem (LDRItem): The item to compute the hash of

    __KWArgs__

    * algo (str): The hashing algorithm to use
    * buffering (int): The amount of the file to read at a time

    __Returns__

    hash_str (str): The str-ified hash hexdigest
    """

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
    """
    Copy an LDRItem's byte contents from one to another

    __Args__

    1. src (LDRItem): The source LDRItem
    2. dst (LDRItem): The destination LDRItem

    __KWArgs__

    * dst_mode (str): The mode to pass to .open() on the dst
    * buffering (int): The amount of data to load into RAM at a time
    * confirm (bool): Whether or not to confirm the duplication was successful
        via hashing the write stream and the result

    __Returns__

    * confirmation (str||None): Either the matched hash or None
    """
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
                data = src_flo.read(buffering)

    if confirm:
        write_hash = str(write_hasher.hexdigest())
        read_hash = hash_ldritem(dst)
        if write_hash == read_hash:
            confirmation = write_hash

    return confirmation


def copy(src, dst, clobber=False, detection="hash", max_retries=3,
         buffering=1024, confirm=True):
    """
    copy one LDRItem's byte contents into another

    __Args__

    1. src (LDRItem): The source LDRItem
    2. dst (LDRItem): The destination LDRItem

    __KWArgs__

    * detection (str): What metric to use to determine equivalence
    * max_retries (int): How many times to retry at max on a bad copy
    * buffering (int): How much of anything to load into RAM at once
    * confirm (bool): Whether or not to confirm the copy by hashing
        the write stream and the resulting copy

    __Returns__

    * cr (CopyReport): A stub class loaded with fields
    * _OR_
    * "BADCOPY" if things went really wrong
    """

    class CopyReport(object):
        """
        stub class to carry info out of this function
        """
        def __init__(self):
            self.src_eq_dst = None
            self.copied = False
            self.confirmed = False
            self.dst_existed = None
            self.clobbered_dst = None
            self.src_hash = None
            self.dst_hash = None

    supported_detections = [
        "hash",
        "name"
    ]

    if detection not in supported_detections:
        raise ValueError("{} is not a supported clobber " +
                         "detection scheme.".format(str(detection)))

    cr = CopyReport()

    if dst.exists():
        if not clobber:
            cr.dst_existed = True
            cr.clobbered_dst = False
            return cr
        else:  # Clobber stuff
            if detection is "hash":
                s_hash = hash_ldritem(src)
                d_hash = hash_ldritem(dst)
                if s_hash == d_hash:  # Its got the same hash, don't copy anything its already the same
                    cr.src_eq_dst = True
                    cr.copied = False
                    cr.confirmed = True
                    cr.dst_existed = True
                    cr.clobbered_dst = False
                    cr.src_hash = s_hash
                    cr.dst_hash = d_hash
                    return cr
            elif detection is "name":
                if src.item_name == dst.item_name:  # Its got the same name, don't copy anything its already the same
                    cr.src_eq_dst = True
                    cr.copied = False
                    cr.confirmed = False
                    cr.dst_existed = True
                    cr.clobbered_st = False
                    return cr
            else:  # Some mismatch between these impl ifs and the array at the top
                raise AssertionError("ldr item copy func error")

            while max_retries > -1:
                max_retries = max_retries - 1
                if not confirm:  # Fly by the seat of our pants, don't check anything just copy the bytes
                    duplicate_ldritem(
                        src,
                        dst,
                        buffering=buffering,
                        confirm=False
                    )
                    cr.copied = True
                    cr.dst_existed = True
                    cr.clobbered_dst = True
                    return cr
                else:
                    c = duplicate_ldritem(src, dst, buffering=buffering, confirm=True)
                    if c is not None:
                        cr.src_eq_dst = True
                        cr.copied = True
                        cr.confirmed = True
                        cr.dst_existed = True
                        cr.clobbered_dst = True
                        cr.src_hash = c
                        cr.dst_hash = c
                        return cr
    else:  # The dst doesn't exist
        while max_retries > -1:
            max_retries = max_retries - 1
            if not confirm:  # Fly by the seat of our pants, don't check anything just copy the bytes
                duplicate_ldritem(src, dst, buffering=buffering, confirm=False)
                cr.copied = True
                cr.dst_existed = False
                cr.clobbered_dst = False
                return cr
            else:
                c = duplicate_ldritem(
                    src,
                    dst,
                    buffering=buffering,
                    confirm=True
                )
                if c is not None:
                    cr.src_eq_dst = True
                    cr.copied = True
                    cr.confirmed = True
                    cr.dst_existed = False
                    cr.clobbered_dst = False
                    cr.src_hash = c
                    cr.dst_hash = c
                    return cr
    return "BADCOPY"
