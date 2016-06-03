
from abc import ABCMeta, abstractmethod, abstractproperty

__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class Auditor(metaclass=ABCMeta):
    """The Auditor class is an abstract class for all auditor concrete classes
    """
    def get_subject(self):
        """returns the subject data attribute
        """
        return self._subject

    def set_subject(self, value):
        """sets the data attribute of the auditor class
        """
        self.subject = value

    def get_errorpackager(self):
        """returns the errorpackager data attribute
        """
        return self._errorpackager

    def set_errorpackager(self, value):
        """sets the errorpackager data attribute
        """
        self._errorpackager = value

    @abstractmethod
    def audit():
        """an abstract method requiring an implementation for how to audit the subject.
        It should return a boolean value
        """
        pass

    subject = abstractproperty(get_subject, set_subject)
    errorpackager = abstractproperty(
        get_errorpackager, set_errorpackager)
