from sys import stderr

from .archive import Archive
from .abc.auditor import Auditor
from .accessionrecordauditor import AccessionRecordAuditor
from .errorpackager import ErrorPackager
from .fitsauditor import FitsAuditor
from .premisauditor import PremisAuditor


class ArchiveAuditor(Auditor):
    def __init__(self, source_directory, the_subject):
        self.source = source_directory
        self.subject = the_subject
        self.errorpackager = ErrorPackager()
        self.fitsauditor = FitsAuditor
        self.premisauditor = PremisAuditor
        self.accessionrecordauditor = AccessionRecordAuditor

    def get_subject(self):
        return self._subject

    def set_subject(self, value):
        if isinstance(value, Archive):
            self._subject = value
        else:
            raise ValueError("ArchiveAuditor can only audit a subject " +
                             "that is an Archive instance")

    def get_errorpackager(self):
        return self._errorpackager

    def set_errorpackager(self, value):
        self._errorpackager = value

    def audit(self):

        for n_segment in self.subject.segment_list:
            print(n_segment.identifier)
            for n_msuite in n_segment.materialsuite_list:
                premis_auditor = self.premisauditor(n_msuite.premis).audit()
                for n_techmd in n_msuite.technicalmetadata_list:
                    tech_auditor = self.fitsauditor(n_techmd).audit()
                    print(tech_auditor)
                print(n_msuite.presform_list)


        # for n_record in self.subject.accessionrecord_list:

        #     accession_audit = self.accessionrecordauditor(n_record).audit()
        #     if not accession_audit:
        #         stderr.write(accession_audit.show_errors())
        #         raise ValueError(
        #             "{} is not a valid accession record".format(
        #                 n_record.item_name)
        #             )
        #     else:
        #         print("hi")

        # for n_segment in self.subject.segment_list:
        #     for n_msuite in n_segment.materialsuite_list:
        #         premisaudit = self.premisauditor(n_msuite.premis)
        #         if not premisaudit.audit():
        #             stderr.write(premisaudit.show())
        #             raise ValueError(
        #                 "{} is not a valid premis record".format(
        #                     n_msuite.premis.item_name))
        #         for n_techmd in n_msuite.technicalmetadata_list:
        #             fitsaudit = self.fitsauditor(n_techmd).audit()
        #             if not fitsaudit:
        #                 stderr.write(fitsaudit.show())
        #                 raise ValueError(
        #                     "{} is not a valid fits record".format(
        #                         n_techmd.item_name))

        #         if getattr(n_msuite, 'presform_list', None) is not None:
        #             for n_presform in n_msuite.presform_list:
        #                 premisaudit = self.premisauditor(n_presform.premis)
        #                 if not premisaudit.audit():
        #                     stderr.write(premisaudit.show_errors())
        #                     raise ValueError(
        #                         "{} is not valid premis".format(
        #                             n_presform.premis.item_name))
        #                 n_presform_tmd_list = n_presform.technicalmetadata_list
        #                 for tmd in n_presform_tmd_list:
        #                     fitsaudit = self.fitsauditor(tmd).audit()
        #                     if not fitsaudit:
        #                         stderr.write(fitsaudit.show_errors())
        #                         raise ValueError(
        #                             "{} is not valid fits".format(
        #                                 tmd.item_name))
        return True

    def show_errors(self):
        return self.errors.display()

    subject = property(get_subject, set_subject)
    errorpackager = property(get_errorpackager, set_errorpackager)
