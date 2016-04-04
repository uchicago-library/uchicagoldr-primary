class App(object):
    """
    The base class for all applications

    __KWArgs__

    * __author__ (str): The author's name
    * __email__ (str): The author's email
    * __company__ (str): The author's company
    * __copyright__ (str): A copyright notice
    * __publication__ (str): A publication date (ISO8601)
    * __version__ (str): A version number
    """
    def __init__(self, __author__=None, __email__=None, __company__=None,
                 __copyright__=None, __publication__=None, __version__=None):
        self.__author__ = __author__
        self.__email__ = __email__
        self.__company__ = __company__
        self.__copyright__ = __copyright__
        self.__publication__ = __publication__
        self.__version__ = __version__
        self.config = None
        # Do whatever it is this application does
        self.main()

    def main(self):
        raise NotImplemented()
