
from sys import stderr

from .abc.auditor import Auditor
from .accessionrecordauditor import AccessionRecordAuditor
from .errorpackager import ErrorPackager
from .fitsauditor import FitsAuditor
from .premisauditor import PremisAuditor
from .stage import Stage

__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class StageAuditor(Auditor):
    """The StageAuditor class should be used to check that a given Stage
    structure is complete to be useful for the LDR.
    """
    def __init__(self, the_subject):
        """initializes a StageAuditor object

        __Args__
        1. subject (Structure): the Stage structure instance that
        needs to be audited
        """
        self.subject = the_subject
        self.errorpackager = ErrorPackager()
        self.accessionrecordauditor = AccessionRecordAuditor
        self.premisauditor = PremisAuditor
        self.fitsauditor = FitsAuditor

    def get_subject(self):
        """returns the subject data attribute
        """
        return self._subject

    def set_subject(self, value):
        """sets the subject data attribute value
        """
        if isinstance(value, Stage):
            self._subject = value
        else:
            raise ValueError("StageAuditor can only audit a subject " +
                             "that is an Archive instance")

    def get_errorpackager(self):
        """returns the errorpackger data attribute value
        """
        return self._errorpackager

    def set_errorpackager(self, value):
        """sets the errorpackager data attribute
        """
        self._errorpackager = value

    def audit(self):
        """returns a boolean value

        checks if the accessionrecord is complete, checks that the
        materialsuites contain valid premis, and contain valid technical
        metadata,

        """
        for n_record in self.subject.accessionrecord_list:
            accession_audit = self.accessionrecordauditor(n_record).audit()
            if not accession_audit:
                stderr.write(accession_audit.show_errors())
                raise ValueError(
                    "{} is not a valid accession record".format(
                        n_record.item_name)
                    )
        for n_segment in self.subject.segment_list:
            for n_msuite in n_segment.materialsuite_list:
                premisaudit = self.premisauditor(n_msuite.premis)
                if not premisaudit.audit():

                    stderr.write(premisaudit.show())
                    raise ValueError(
                        "{} is not a valid premis record".format(
                            n_msuite.premis.item_name))
                for n_techmd in n_msuite.technicalmetadata_list:
                    fitsaudit = self.fitsauditor(n_techmd).audit()
                    if not fitsaudit:
                        stderr.write(fitsaudit.show())
                        raise ValueError(
                            "{} is not a valid fits record".format(
                                n_techmd.item_name))
                if getattr(n_msuite, 'presform_list', None) is not None:
                    for n_presform in n_msuite.presform_list:
                        premisaudit = self.premisauditor(n_presform.premis)
                        if not premisaudit.audit():
                            stderr.write(premisaudit.show_errors())
                            raise ValueError(
                                "{} is not valid premis".format(
                                    n_presform.premis.item_name))
                        n_presform_tmd_list = n_presform.technicalmetadata_list
                        for tmd in n_presform_tmd_list:
                            fitsaudit = self.fitsauditor(tmd).audit()
                            if not fitsaudit:
                                stderr.write(fitsaudit.show_errors())
                                raise ValueError(
                                    "{} is not valid fits".format(
                                        tmd.item_name))
        return True

    def show_errors(self):
        """returns the errors that may have resulted from the audit
        """
        return self.errors.display()

    subject = property(get_subject, set_subject)
    errorpackager = property(get_errorpackager, set_errorpackager)
