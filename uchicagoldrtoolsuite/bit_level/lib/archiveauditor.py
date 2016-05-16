

from .archive import Archive
from abc.auditor import Auditor


class ArchiveAuditor(Auditor):
    def __init__(self, the_subject):
        self.subject = the_subject

    def get_subject(self):
        return self._subject

    def set_subject(self, value):
        if isinstance(value, Archive):
            self._subject = value
        else:
            raise ValueError("ArchiveAuditor can only audit a subject " +
                             "that is an Archive instance")

    def audit(self):
        return True

    subject = property(get_subject, set_subject)
