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
                buf = read_file.read(1024 * 1000 * 100)
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
                buf = read_file.read(1024 * 1000 * 100)
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


def move(src, dst, clobber=False, eq_detect='bytes'):
    """
    a variation on copy which rather than merely copy the byte-stream of
    the origin into the destination and deletes the origin

    __Args__

    1. origin_loc (LDRItem): origin_loc is the source data to move
    2. destination_loc (LDRItem): destination_loc is where the source
    should be moved
    """
    c = LDRItemCopier(src, dst, clobber=clobber, eq_detect=eq_detect)
    r = c.copy()
    if not r['src_eqs_dst']:
        raise OSError("src != dst")
    origin_loc.delete(final=True)
    if not src.exists() and dst.exists():
        return True
    else:
        return False

def hash_ldritem(ldritem, algo="md5", buffering=1024*1000*100):
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


