
from hashlib import md5
from os.path import join, split
from urllib.request import urlopen, URLError
from uuid import uuid1

from .abc.ldritem import LDRItem
from .idbuilder import IDBuilder
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


def get_an_agent_id(id_string):
    def get_premis_agents_file():
        this_dir, this_filename = split(__file__)
        return join(this_dir, 'premis', 'agents.txt')

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
