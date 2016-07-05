from .abc.ldritem import LDRItem
from .ldritemoperations import hash_ldritem


class LDRItemCopier(object):
    """
    An environment for facilitating qualified copies of LDRItem instances
    """
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
        self.src = src
        self.dst = dst
        self.clobber = clobber
        self.eq_detect = eq_detect
        self.max_retries = max_retries
        self.buffering = buffering

    def get_src(self):
        return self._src

    def set_src(self, src):
        if not isinstance(src, LDRItem):
            raise ValueError()
        self._src = src

    def get_dst(self):
        return self._dst

    def set_dst(self, dst):
        if not isinstance(dst, LDRItem):
            raise ValueError()
        self._dst = dst

    def get_clobber(self):
        return self._clobber

    def set_clobber(self, clobber):
        if not isinstance(clobber, bool):
            raise ValueError()
        self._clobber = clobber

    def get_eq_detect(self):
        return self._eq_detect

    def set_eq_detect(self, eq_detect):
        supported_detections = [
            "bytes",
            "name",
            "hash",
            "size"
        ]

        if not isinstance(eq_detect, str):
            raise ValueError()
        if eq_detect not in supported_detections:
            raise ValueError(
                "eq_detect must be in {}".format(str(supported_detections))
            )
        self._eq_detect = eq_detect

    def get_max_retries(self, max_retries):
        return self._max_retries

    def set_max_retries(self, max_retries):
        if not isinstance(max_retries, int):
            raise ValueError()
        self._max_retries = max_retries

    def get_buffering(self):
        return self._buffering

    def set_buffering(self, buffering):
        if not isinstance(buffering, int):
            raise ValueError()
        self._buffering = buffering

    def get_confirm(self):
        return self._confirm

    def set_confirm(self, confirm):
        if not isinstance(confirm, bool):
            raise ValueError()
        self._confirm = confirm

    def are_the_same(self):
        """
        Dispatch to the proper comparing function

        __Returns__

        (bool): comparison functions should return a bool
        """
        if self.eq_detect == "bytes":
            return self.ldritem_equal_byte_contents()
        elif self.eq_detect == "hash":
            return self.ldritem_equal_contents_hash()
        elif self.eq_detect == "name":
            return self.ldritem_equal_names()
        elif self.eq_detect == "size":
            return self.ldritem_equal_contents_size()
        else:
            raise AssertionError(
                "How did we get this far without setting eq_detect " +
                "to something valid?"
            )

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
        r = self.build_report_dict()
        r['copied'] = False
        if self.dst.exists():
            r['dst_existed'] = True
            if not self.clobber:
                # Not Clobbering
                r['clobbered_dst'] = False
                return r
            elif self.are_the_same():
                # No copy required
                r['clobbered_dst'] = False
                r['src_eqs_dst'] = True
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
                complete = self.are_the_same()
            except Exception as e:
                ex = e
        if complete:
            r['src_eqs_dst'] = True
            r['copied'] = True
            return r
        else:
            if not eat_exceptions:
                raise OSError("!!! BAD COPY !!! - {} - COPY NOT COMPLETE".format(str(ex)))
                raise ex
            else:
                return r

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
                    return False
        return True

    def ldritem_equal_contents_size(self):
        if self.src.get_size(buffering=self.buffering) == \
                self.dst.get_size(buffering=self.buffering):
            return True
        return False

    def ldritem_equal_contents_hash(self):
        """
        Determines if src and dst are equivalent via hashing both

        __Returns__

        (bool): True if equivalent, otherwise False
        """
        if hash_ldritem(self.src) == hash_ldritem(self.dst):
            return True
        return False

    def ldritem_equal_names(self):
        """
        Determines if src and dst are equivalent via item_name

        __Returns__

        (bool): True if equivalent, otherwise False
        """
        if self.src.item_name == self.dst.item_name:
            return True
        return False

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
