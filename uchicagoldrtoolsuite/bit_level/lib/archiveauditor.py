
from pypremis.lib import PremisRecord
from xml.etree import ElementTree


from hierarchicalrecord.hierarchicalrecord import HierarchicalRecord

from .archive import Archive
from .abc.auditor import Auditor
from .errorpackager import ErrorPackager
from .ldritemoperations import read_metadata_from_file_object


class ArchiveAuditor(Auditor):
    def __init__(self, source_directory, the_subject):
        self.source = source_directory
        self.subject = the_subject
        self.errors = ErrorPackager()

    def get_subject(self):
        return self._subject

    def set_subject(self, value):
        if isinstance(value, Archive):
            self._subject = value
        else:
            raise ValueError("ArchiveAuditor can only audit a subject " +
                             "that is an Archive instance")

    def audit_premis(self, a_msuite):
        instantiated_object = read_metadata_from_file_object(
            'premis', PremisRecord, msuite=a_msuite)
        if instantiated_object is None:
            self.errors.add(
                "file",
                "premis record for {}".format(a_msuite.content.item_name) +
                " is missing")
            return False

        record_events = instantiated_object.get_events_list
        if len(record_events) < 2:
            self.errors.add(
                "premis",
                "premis record for {} ".format(a_msuite.content.item_name) +
                " has less than 2 events.")
        for obj in instantiated_object.get_object_list():
            for storage in obj.get_storage():
                if not storage.get_contentLocation():
                    self.errors.add(
                        "premis",
                        "premis record for {}".format(
                            a_msuite.content.item_name) +
                        " is missing a contentLocation")
            for characteristic in obj.getCharacteristics():
                fixities = [characteristic.get_fixitiy()]
                if len(fixities) == 0:
                    self.errors.add(
                        "premis",
                        "premis record for {}".format(
                            a_msuite.content.item_name) +
                        " is missing fixity information")
        if len(self.errors) > 0:
            return False
        else:
            return True

    def audit_fitsmd(self, a_msuite):
        instantiated_object = read_metadata_from_file_object(
            'techmd', ElementTree.parse, msuite=a_msuite)
        if instantiated_object is None:
            self.errors.add(
                "file",
                "no fits record {}".format(a_msuite.content.item_name))
        root_of_xml_object = instantiated_object.get_root()
        filePath = root_of_xml_object.find(
            '{http://hul.harvard.edu/ois/xml/ns/fits/fits_output}fileInfo/' +
            '{ http://hul.harvard.edu/ois/xml/ns/fits/fits_output}filePath')
        metadata = root_of_xml_object.find(
            '{http://hul.harvard.edu/ois/xml/ns/fits/fits_output}metadata')
        if metadata is None:
            self.errors.add(
                "fits",
                "fits metadata record for {}".format(
                    a_msuite.content.item_name) +
                " is missing a metadata node")
        if filePath is None:
            self.errors.add(
                "fits",
                "fits record for {} ".format(a_msuite.content.item_name) +
                " is missing a filePath element")
        if len(self.errors) > 0:
            return False
        else:
            return True

    def audit_accessionrecord(self, an_ldr_item):
        instantiated_object = read_metadata_from_file_object(
            'accessionrecord', HierarchicalRecord, ldritem=an_ldr_item)
        required_fields = [
            'AccessionNumber', 'OrganizatioName', 'Summary', 'CollectionTitle',
            'EADID', 'Rights', 'Restrictions', 'RestrictionComments', 'Origin',
            'Access', 'Discover', 'AdministrativeComments', 'AccessDescription'
        ]
        fields_in_record = instantiated_object.keys()
        check_field_existence = [
            x for x in fields_in_record if x not in required_fields
        ]
        if len(check_field_existence) > 0:
            self.errors.add("accessionrecord",
                            "accession record is missing " +
                            "the following fields " +
                            "{}".format(', '.join(check_field_existence)))
        if len(self.errors) > 0:
            return False
        else:
            return True

    def audit(self):
        if getattr(self.subject, 'accessionrecord_list', None) == []:
            self.errors.add("record", "missing accession record")

        audit_results = []
        for n_record in self.subject.accessionrecord_list:
            audit_results.append(self.audit_accessionrecord(n_record))

        for n_segment in self.subject.segment_list:
            for n_msuite in n_segment.materialsuite_list:

                audit_results.append(self.audit_premis(n_msuite))
                audit_results.append(self.audit_fitsmd(n_msuite))
                if getattr(n_msuite, 'presform_list', None) is not None:
                    for n_presform in n_msuite.presform_list:
                        audit_results.append(self.audit_premis(n_presform))
                        audit_results.append(self.audit_fitsmd(n_presform))
        if len([x for x in audit_results if x is False]) > 0:
            return False
        else:
            return True

    def show_errors(self):

        return self.errors.display()

    subject = property(get_subject, set_subject)
