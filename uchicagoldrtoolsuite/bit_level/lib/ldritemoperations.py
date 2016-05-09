from hashlib import md5

from ...core.lib.convenience import sane_hash
from .abc.ldritem import LDRItem


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


def move(origin_loc, destination_loc):
    raise NotImplemented('yet')


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
    if not isinstance(origin_loc, LDRItem) or not \
            isinstance(destination_loc, LDRItem):
        raise TypeError("must pass two instances of LDRPathRegularFile" +
                        " to the copy function.")
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
