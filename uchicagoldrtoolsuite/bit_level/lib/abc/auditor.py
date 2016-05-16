
from abc import ABCMeta, abstractmethod, abstractproperty


class Auditor(metaclass=ABCMeta):

    def get_subject(self):
        return self._subject

    def set_subject(self, value):
        self.subject = value

    @abstractmethod
    def audit():
        pass

    subject = abstractproperty(get_subject, set_subject)
