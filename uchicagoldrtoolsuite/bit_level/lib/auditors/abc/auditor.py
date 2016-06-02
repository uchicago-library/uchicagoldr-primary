
from abc import ABCMeta, abstractmethod, abstractproperty


class Auditor(metaclass=ABCMeta):

    def get_subject(self):
        return self._subject

    def set_subject(self, value):
        self.subject = value

    def get_errorpackager(self):
        return self._errorpackager

    def set_errorpackager(self, value):
        self._errorpackager = value

    @abstractmethod
    def audit():
        pass

    subject = abstractproperty(get_subject, set_subject)
    errorpackager = abstractproperty(
        get_errorpackager, set_errorpackager)
