from sys import stderr

from ..structures.archive import Archive
from .abc.auditor import Auditor
from .accessionrecordauditor import AccessionRecordAuditor
from .errorpackager import ErrorPackager
from .fitsauditor import FitsAuditor
from .premisauditor import PremisAuditor

__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class ArchiveAuditor(Auditor):
    """The ArchiveAuditor object is meant to evaluate an archive structure
    for completeness. It analyzes every fits, premis and accession record
    in the structure for readiness to be archived.
    """
    def __init__(self, the_subject):
        """returns an instance of ArchiveAuditor

        __Args__
        1. subject (Structure): the structure that needs to be audited
        """
        self.subject = the_subject
        self.errorpackager = ErrorPackager()
        self.fitsauditor = FitsAuditor
        self.premisauditor = PremisAuditor
        self.accessionrecordauditor = AccessionRecordAuditor

    def get_subject(self):
        """returns the subject of the auditor
        """
        return self._subject

    def set_subject(self, value):
        """sets the subject of the auditor. It will fail if
        the subject is not an Archive structure instance
        """
        if isinstance(value, Archive):
            self._subject = value
        else:
            raise ValueError(
                "ArchiveAuditor can only audit a subject that is an" +
                " Archive instance")

    def get_errorpackager(self):
        """returns the errorpackager
        """
        return self._errorpackager

    def set_errorpackager(self, value):
        """sets the errorpackage instance for the auditorr
        """
        if getattr(self, '_errorpackager', None) is not None:
            self._errorpackager = ErrorPackager()
        else:
            pass

    def audit(self):
        """returns a boolean value

        This function performs the following checks

        1. checks that the accessionrecord is validate
        2. checks that every premis record is valid
        3. checks that every fits record is valid
        """
        total_files = 0
        for n_segment in self.subject.segment_list:
            for n_record in self.subject.accessionrecord_list:
                if getattr(n_record, 'content', None) is not None:
                    total_files += 1
                accession_audit = self.accessionrecordauditor(n_record).audit()
                if not accession_audit:
                    stderr.write(accession_audit.show_errors())
                    raise ValueError(
                        "{} is not a valid accession record".format(
                            n_record.item_name)
                    )
            for n_msuite in n_segment.materialsuite_list:
                premisaudit = self.premisauditor(
                    n_msuite.premis).audit()
                if not premisaudit:
                    stderr.write(premisaudit.show_errors())
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

                if getattr(n_msuite, 'presform_list', None):
                    for n_presform in n_msuite.presform_list:
                        if getattr(n_presform, 'content', None) is not None:
                            total_files += 1
                        premisaudit = self.premisauditor(
                            n_presform.premis).audit()
                        for n_techmd in n_presform.technicalmetadata_list:
                            fitsaudit = self.fitsauditor(n_techmd).audit()
                            if not fitsaudit:
                                stderr.write(fitsaudit.show_errors())
                                raise ValueError(
                                    "{} is not valid fits".format(
                                        n_techmd.item_name))
        if total_files == 0:
            return False
        return True

    def show_errors(self):
        """returns a list of the errors found in an audit
        """
        return self.errors.display()

    subject = property(get_subject, set_subject)
    errorpackager = property(get_errorpackager, set_errorpackager)
