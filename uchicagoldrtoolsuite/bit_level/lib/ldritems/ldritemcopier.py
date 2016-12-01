from json import dumps
from logging import getLogger

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, \
    log_init_success
from .abc.ldritem import LDRItem
from .ldritemoperations import hash_ldritem


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class LDRItemCopier(object):
    """
    An environment for facilitating qualified copies of LDRItem instances
    """
    @log_aware(log)
    def __init__(self, src, dst, clobber=False, eq_detect='bytes',
                 max_retries=3, buffering=1024*1000*100):
        """
        Spawn a new copier

        __Args__
        1. src (LDRItem): The source item
        2. dst (LDRItem): The destination item

        __KWArgs__
        * clobber (bool): Whether or not to clobber an existing dst
        * eq_detect (str): what method to use to detect equality
            of the src and dst
        * max_retries (int): How many times to attempt a copy operation
            before giving up
        * buffering (int): How many bytes to load into RAM for copying/
            comparison operations
        """
        log_init_attempt(self, log, locals())
        self.src = src
        self.dst = dst
        self.clobber = clobber
        self.eq_detect = eq_detect
        self.max_retries = max_retries
        self.buffering = buffering
        log_init_success(self, log)

    @log_aware(log)
    def __repr__(self):
        attrib_dict = {
            'src': str(self.src),
            'dst': str(self.dst),
            'clobber': self.clobber,
            'eq_detect': self.eq_detect,
            'max_retries': self.max_retries,
            'buffering': self.buffering
        }
        return "<LDRItemCopier {}".format(dumps(attrib_dict, sort_keys=True))

    @log_aware(log)
    def get_src(self):
        return self._src

    @log_aware(log)
    def set_src(self, src):
        if not isinstance(src, LDRItem):
            raise ValueError("src must be LDRItem, not {}".format(type(src)))
        self._src = src

    @log_aware(log)
    def get_dst(self):
        return self._dst

    @log_aware(log)
    def set_dst(self, dst):
        if not isinstance(dst, LDRItem):
            raise ValueError("dst must be LDRItem, not {}".format(type(dst)))
        self._dst = dst

    @log_aware(log)
    def get_clobber(self):
        return self._clobber

    @log_aware(log)
    def set_clobber(self, clobber):
        if not isinstance(clobber, bool):
            raise ValueError()
        self._clobber = clobber

    @log_aware(log)
    def get_eq_detect(self):
        return self._eq_detect

    @log_aware(log)
    def set_eq_detect(self, eq_detect):
        supported_detections = [
            "bytes",
            "name",
            "md5",
            "crc32",
            "adler32",
            "sha256",
            "size"
        ]

        if not isinstance(eq_detect, str):
            raise ValueError()
        if eq_detect not in supported_detections:
            raise ValueError(
                "eq_detect must be in {}".format(str(supported_detections))
            )
        self._eq_detect = eq_detect

    @log_aware(log)
    def get_max_retries(self, max_retries):
        return self._max_retries

    @log_aware(log)
    def set_max_retries(self, max_retries):
        if not isinstance(max_retries, int):
            raise ValueError()
        self._max_retries = max_retries

    @log_aware(log)
    def get_buffering(self):
        return self._buffering

    @log_aware(log)
    def set_buffering(self, buffering):
        if not isinstance(buffering, int):
            raise ValueError()
        self._buffering = buffering

    @log_aware(log)
    def get_confirm(self):
        return self._confirm

    @log_aware(log)
    def set_confirm(self, confirm):
        if not isinstance(confirm, bool):
            raise ValueError()
        self._confirm = confirm

    @log_aware(log)
    def are_the_same(self, eq_detect=None):
        """
        Dispatch to the proper comparing function

        __KWArgs__

        * eq_detect (str): The equality metric to use, defaults to the
            same as the Copier instance of not supplied.

        __Returns__

        (bool): comparison functions should return a bool
        """

        if eq_detect is None:
            eq_detect = self.eq_detect

        log.debug(
            "Equality delegator called for {} and {} with metric {}".format(
                self.src.item_name, self.dst.item_name, eq_detect
            )
        )

        # Metrics go from least paranoid to most paranoid, generally
        # Choosing a metric has a significant effect on the amount of time
        # copies will take, either in aggregate or of large files.
        equality_metrics = {
            'adler32': self.ldritem_equal_contents_adler32,
            'crc32': self.ldritem_equal_contents_crc32,
            'md5': self.ldritem_equal_contents_md5,
            'sha256': self.ldritem_equal_contents_sha256,
            'bytes': self.ldritem_equal_byte_contents
        }

        metric = equality_metrics.get(eq_detect)

        if metric is None:
            raise ValueError(
                "{} isn't a valid equality metric!".format(eq_detect)
            )
        else:
            return metric()

    @log_aware(log)
    def copy(self, eat_exceptions=False):
        """
        Respecting user options and comparisons copy the file so the src
        is equivalent to the dst, if possible

        __KWArgs__

        * eat_exceptions (bool): If True never raise an exception, instead
            return a report even if the copy raises an exception.

        __Returns__

        (dict): A small informational dict
        """
        log.debug("Attempting to copy {} to {} (eat_exceptions={})".format(
            self.src.item_name, self.dst.item_name, str(eat_exceptions)))
        r = self.build_report_dict()
        r['copied'] = False
        if self.dst.exists():
            r['dst_existed'] = True
            if not self.clobber:
                # Not Clobbering
                r['clobbered_dst'] = False
                log.debug("{}".format(dumps(r)))
                return r
            elif self.are_the_same():
                # No copy required
                r['clobbered_dst'] = False
                r['src_eqs_dst'] = True
                log.debug("{}".format(dumps(r)))
                return r
            else:
                r['clobbered_dst'] = True
        else:
            r['dst_existed'] = False

        complete = False
        i = 0
        ex = None
        while not complete and i < self.max_retries:
            i += 1
            try:
                with self.src.open('rb') as s1:
                    with self.dst.open('wb') as s2:
                        data = s1.read(self.buffering)
                        while data:
                            s2.write(data)
                            data = s1.read(self.buffering)
                # If we have to take a copy operation don't use any metric
                # other than a direct bytes comparison to audit the copy
                complete = self.are_the_same(eq_detect="bytes")
            except Exception as e:
                log.warn("An exception occured while the copier was " +
                         "attempting to copy a file: {}.".format(str(e)) +
                         "If this error occured before reaching max_retries " +
                         "the copy will be attempted again. Otherwise an " +
                         "exception will be raised if this was a vital copy.")
                ex = e
        if complete:
            r['src_eqs_dst'] = True
            r['copied'] = True
            log.debug("{}".format(dumps(r)))
            return r
        else:
            if not eat_exceptions:
                raise OSError("!!! BAD COPY !!! - {} - COPY NOT COMPLETE - {} !=  {} (metric: {})".format(str(ex), self.src.item_name, self.dst.item_name, self.eq_detect))
            else:
                log.warn("{}".format(dumps(r)))
                return r

    @log_aware(log)
    def ldritem_equal_byte_contents(self):
        """
        Grab substrings of byte content from each item and compare them,
        if they're different return False, otherwise return True

        __Returns__

        (bool): True if equivalent, otherwise False
        """
        # The scale of this function means it has to be pretty streamlined,
        # think hard/benchmark before monkeying around with stuff in here
        # Grab streams
        log.debug("Checking byte equality of {} and {}".format(
            self.src.item_name, self.dst.item_name))
        with self.src.open() as s1:
            with self.dst.open() as s2:
                # Grab initial data
                data1 = s1.read(self.buffering)
                data2 = s2.read(self.buffering)
                while data1 and data2:
                    # Compare
                    if data1 != data2:
                        return False
                    # Grab the next set of blocks
                    data1 = s1.read(self.buffering)
                    data2 = s2.read(self.buffering)
                if data1 and not data2 or \
                        data2 and not data1:
                    log.debug("{} != {} (bytes)".format(
                        self.src.item_name, self.dst.item_name))
                    return False
        log.debug("{} == {} (bytes)".format(
            self.src.item_name, self.dst.item_name))
        return True

    @log_aware(log)
    def ldritem_equal_contents_size(self):
        log.debug("Checking size equality of {} and {}".format(
            self.src.item_name, self.dst.item_name))
        if self.src.get_size(buffering=self.buffering) == \
                self.dst.get_size(buffering=self.buffering):
            log.debug("{} == {} (size)".format(
                self.src.item_name, self.dst.item_name))
            return True
        log.debug("{} != {} (size)".format(
            self.src.item_name, self.dst.item_name))
        return False

    @log_aware(log)
    def ldritem_equal_contents_hash(self, x):
        """
        Determines if src and dst are equivalent via hashing both

        __Returns__

        (bool): True if equivalent, otherwise False
        """
        log.debug("Checking hash equality of {} and {}".format(
            self.src.item_name, self.dst.item_name))
        if hash_ldritem(self.src, x) == hash_ldritem(self.dst, x):
            log.debug("{} == {} (hash)".format(
                self.src.item_name, self.dst.item_name))
            return True
        log.debug("{} != {} ({})".format(
            self.src.item_name, self.dst.item_name, str(x)))
        return False

    @log_aware(log)
    def ldritem_equal_contents_adler32(self):
        return self.ldritem_equal_contents_hash('adler32')

    @log_aware(log)
    def ldritem_equal_contents_crc32(self):
        return self.ldritem_equal_contents_hash('crc32')

    @log_aware(log)
    def ldritem_equal_contents_sha256(self):
        return self.ldritem_equal_contents_hash('sha256')

    @log_aware(log)
    def ldritem_equal_contents_md5(self):
        return self.ldritem_equal_contents_hash('md5')

    @log_aware(log)
    def ldritem_equal_names(self):
        """
        Determines if src and dst are equivalent via item_name

        __Returns__

        (bool): True if equivalent, otherwise False
        """
        log.debug("Checking name equality of {} and {}".format(
            self.src.item_name, self.dst.item_name))
        if self.src.item_name == self.dst.item_name:
            log.debug("{} == {} (name)".format(
                self.src.item_name, self.dst.item_name))
            return True
        log.debug("{} != {} (name)".format(
            self.src.item_name, self.dst.item_name))
        return False

    @log_aware(log)
    def build_report_dict(self, copied=None, dst_existed=None,
                          clobbered_dst=None, src_eqs_dst=None):
        """
        Build the report dict returned by the .copy() function

        __Returns__

        (dict): The little report
        """
        x = {}
        x['eq_detect'] = self.eq_detect
        x['clobber_setting'] = self.clobber
        x['src_eqs_dst'] = src_eqs_dst
        x['copied'] = copied
        x['dst_existed'] = dst_existed
        x['clobbered_dst'] = clobbered_dst
        return x

    src = property(get_src, set_src)
    dst = property(get_dst, set_dst)
    clobber = property(get_clobber, set_clobber)
    eq_detect = property(get_eq_detect, set_eq_detect)
    max_retires = property(get_max_retries, set_max_retries)
    buffering = property(get_buffering, set_buffering)
    confirm = property(get_confirm, set_confirm)
