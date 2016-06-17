
from os import makedirs
from os.path import basename, dirname, exists, join, split
from sys import stderr

from uchicagoldrtoolsuite.core.lib.idbuilder import IDBuilder

from .abc.archiveserializationwriter import ArchiveSerializationWriter
from ..structures.archive import Archive
from ..misc.accessionrecordmodifier import AccessionRecordModifier
from ..misc.archivefitsmodifier import ArchiveFitsModifier
from ..misc.archivemanifestwriter import ArchiveManifestWriter
from ..misc.archivepremismodifier import ArchivePremisModifier

from ..auditors.archiveauditor import ArchiveAuditor
from ..ldritems.ldritemcopier import LDRItemCopier
from ..ldritems.ldrpath import LDRPath
from ..fstools.pairtree import Pairtree
from ..misc.premisdigestextractor import PremisDigestExtractor

from ..misc.premisrestrictionextractor import PremisRestrictionsExtractor


__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class FileSystemArchiveWriter(ArchiveSerializationWriter):
    """
    writes an archive structure to the file system as a directory.

    It is instantited with an instance of an ArchiveStructure,
    the archive root directory, and the origin root directory,

    Once instantiated, the write() method should be called when ready
    to serialize the archive structure to disk.
    """
    def __init__(self, aStructure, archive_loc, origin_loc):
        """
        initialize the writer

        __Args__

        1. aStructure (StagingStructure): The structure to write
        2. archive_loc (str): the root directory for the archive of the ldr
        3. origin_loc (str): the root directory of the stage directory
        being archived
        """
        self.structure = aStructure
        self.pairtree = Pairtree(self.structure.identifier)
        self.audit_qualification = ArchiveAuditor(aStructure)
        self.origin_root = split(origin_loc)[0]
        self.identifier = IDBuilder().build('premisID')
        self.premis_modifier = ArchivePremisModifier
        self.fits_modifier = ArchiveFitsModifier
        self.file_digest_extraction = PremisDigestExtractor
        self.file_restriction_extraction = PremisRestrictionsExtractor
        self.manifest_writer = ArchiveManifestWriter(archive_loc)
        self.archive_loc = archive_loc
        self.accessrecord_modifier = AccessionRecordModifier

    def write(self):
        """
        checks of the structure is validate and audits the contents of the
        structure for errors.

        If the structure is valid and there are no errors in the audit it
        serializes the structure to disk which includes the following steps

        1. modifies premis records in the structure to include archive
        information

        2. modifies fits technical metadata records to include archive
        information

        3. sets up archive file serialization structure and copies contents
        of the structure into the serialization structure

        4. extracts message digests for the resource files from premis records
        and appends them with the new file location to the archive manifest

        """
        if self.structure.validate() and self.audit_qualification.audit():
            pairtree_path = self.pairtree.get_pairtree_path()
            data_dir = join(self.archive_loc, pairtree_path, 'data')
            admin_dir = join(self.archive_loc, pairtree_path, 'admin')
            makedirs(data_dir, exist_ok=True)
            makedirs(admin_dir, exist_ok=True)
            accrecord_dir = join(admin_dir, 'accessionrecord')
            legalnote_dir = join(admin_dir, 'legalnotes')
            adminnote_dir = join(admin_dir, 'adminnotes')
            makedirs(accrecord_dir, exist_ok=True)
            makedirs(legalnote_dir, exist_ok=True)
            makedirs(adminnote_dir, exist_ok=True)
            accrecords = []
            for n_acc_record in self.structure.accessionrecord_list:
                acc_filename = basename(n_acc_record.item_name)
                LDRItemCopier(n_acc_record, LDRPath(
                    join(accrecord_dir,
                         acc_filename))).copy()
                accrecords.append(join(accrecord_dir, acc_filename))
            for n_legal_note in self.structure.legalnote_list:
                legalnote_filename = basename(n_legal_note.item_name)
                LDRItemCopier(n_legal_note, LDRPath(
                    join(legalnote_dir,
                         legalnote_filename))).copy()
            for n_adminnote in self.structure.adminnote_list:
                adminnote_filename = basename(n_adminnote.item_name)
                LDRItemCopier(n_adminnote, LDRPath(
                    join(adminnote_dir,
                         adminnote_filename))).copy()
            accession_restrictions = set([])
            for n_segment in self.structure.segment_list:
                segment_id = n_segment.label+'-'+str(n_segment.run)
                techmd_dir = join(admin_dir, segment_id, 'TECHMD')
                premis_dir = join(admin_dir, segment_id, 'PREMIS')
                segment_data_dir = join(data_dir, segment_id)
                makedirs(techmd_dir, exist_ok=True)
                makedirs(premis_dir, exist_ok=True)
                makedirs(segment_data_dir, exist_ok=True)
                for n_msuite in n_segment.materialsuite_list:
                    n_content_destination_fullpath = join(
                        data_dir, segment_id, n_msuite.content.item_name)

                    modifier = self.premis_modifier(
                        n_msuite.premis, n_content_destination_fullpath)
                    modifier.change_record()
                    digest_data = self.file_digest_extraction(
                        n_msuite.premis).extract_digests()
                    restrictions = self.file_restriction_extraction(
                        n_msuite.premis).extract_restrictions()
                    for n_restriction in restrictions:
                        accession_restrictions.add(n_restriction)
                    self.manifest_writer.add_a_line(
                        n_content_destination_fullpath, digest_data)

                    makedirs(
                        join(data_dir, dirname(
                            n_msuite.content.item_name)), exist_ok=True)
                    makedirs(
                        join(premis_dir, dirname(
                            n_msuite.content.item_name)), exist_ok=True)
                    makedirs(
                        join(techmd_dir, dirname(
                            n_msuite.content.item_name)), exist_ok=True)

                    new_premis_path = join(
                        premis_dir, n_msuite.premis.item_name)
                    new_content_path = join(
                        data_dir, segment_id,
                        n_msuite.content.item_name)

                    makedirs(new_content_path, exist_ok=True)

                    new_content_ldrpath = LDRPath(new_content_path)
                    modifier.record.write_to_file(new_premis_path)
                    LDRItemCopier(n_msuite.content, new_content_ldrpath).copy()

                    for n_techmd in n_msuite.technicalmetadata_list:
                        new_tech_record_loc = join(
                            techmd_dir, n_techmd.item_name)
                        new_tech_record = self.fits_modifier(
                            n_techmd, new_tech_record_loc).modify_record()
                        new_tech_record.write(new_tech_record_loc)
                    if getattr(n_msuite, 'presform_list', None):
                        for n_presform in n_msuite.presform_list:
                            n_destination_fullpath = join(
                                data_dir, segment_id,
                                n_presform.content.item_name)
                            modifier = self.premis_modifier(
                                n_presform.premis, n_destination_fullpath)
                            modifier.change_record()
                            makedirs(
                                join(data_dir, dirname(
                                    n_presform.content.item_name)),
                                exist_ok=True)
                            makedirs(
                                join(premis_dir, dirname(
                                    n_presform.content.item_name)),
                                exist_ok=True)
                            makedirs(
                                join(techmd_dir, dirname(
                                    n_presform.content.item_name)),
                                exist_ok=True)
                            digest_data = self.file_digest_extraction(
                                n_presform.premis).extract_digests()
                            restrictions = self.file_restriction_extraction(
                                n_presform.premis).extract_restrictions()
                            self.manifest_writer.add_a_line(
                                n_destination_fullpath, digest_data)

                            new_premis_path = join(
                                premis_dir, n_presform.premis.item_name)
                            new_presform_content_path = join(
                                data_dir, segment_id,
                                n_presform.content.item_name)
                            new_presform_content_ldrpath = LDRPath(
                                new_presform_content_path)
                            modifier.record.write_to_file(new_premis_path)
                            LDRItemCopier(n_presform.content,
                                 new_presform_content_ldrpath).copy()
                        for n_techmd in n_presform.technicalmetadata_list:
                            new_tech_record_loc = join(
                                techmd_dir, n_techmd.item_name)
                            new_tech_record = self.fits_modifier(
                                n_techmd, new_tech_record_loc).modify_record()

                            new_tech_record.write(new_tech_record_loc)
                self.manifest_writer.write()
                for a_record in accrecords:
                    acc_modifier = self.accessrecord_modifier(
                        LDRPath(a_record))
                    acc_modifier.add_restriction_info(list(restrictions))
                    acc_modifier.write(a_record)

        else:
            stderr.write(self.structure.explain_results())
            stderr.write(self.audit_qualification.show_errors())

    def get_structure(self):
        """returns the structure that this writer serializes
        """
        return self._structure

    def set_structure(self, value):
        """ sets the structure attribute for this writer. It will reject any structure
        object that it not an Archive structure.
        """
        if isinstance(value, Archive):
            self._structure = value
        else:
            raise ValueError(
                "FileSystemArchiveWriter reqiures an Archive structure" +
                " in the structure attribute")

    def get_pairtree(self):
        """returns the pairtree object for the writer
        """
        return self._pairtree

    def set_pairtree(self, value):
        """sets the pairtree object for the writer. It will only accept
        a Pairtree object
        """
        if isinstance(value, Pairtree):
            self._pairtree = value
        else:
            raise ValueError(
                "FileSystemArchiveWriter must take an instance of a " +
                "Pairtree in the pairtree attribute")

    def get_origin_root(self):
        """returns the origin root string for the writer
        """
        return self._origin_root

    def set_origin_root(self, value):
        """sets the origin root for the writer. It will only accept a file
        path that exists on the machine that the code is running on
        """
        if exists(value):
            self._origin_root = value
        else:
            raise ValueError("{} origin root does not exist.".format(value))

    def get_archive_loc(self):
        """returns the archive root of the writer
        """
        return self._archive_loc

    def set_archive_loc(self, value):
        """ sets the archive root for the writer. It will only accept a filepath that
        exists on the machine that the application is running on
        """
        if exists(value):
            self._archive_loc = value
        else:
            raise ValueError(
                "{} archive loc does not exist".format(value))

    def get_identifier(self):
        """ returns the identifer for the writer
        """
        return self._identifier

    def set_identifier(self, value):
        """sets the identifier factory for the writer
        """
        self._identifier = value

    def get_premis_modifier(self):
        """ returns the premis modifier for the writer
        """
        return self._premis_modifier

    def set_premis_modifier(self, value):
        """sets the premis modifier for the writer
        """
        self._premis_modifier = value

    def get_fits_modifier(self):
        """sets the fits modifier for the writer
        """
        return self._fits_modifier

    def set_fits_modifier(self, value):
        """returns the fits modifier for the factory
        """
        self._fits_modifier = value

    structure = property(get_structure, set_structure)
    pairtree = property(get_pairtree, set_pairtree)
    origin_root = property(get_origin_root, set_origin_root)
    archive_loc = property(get_archive_loc, set_archive_loc)
    fits_modifer = property(get_fits_modifier, set_fits_modifier)
    premis_modifier = property(get_premis_modifier, set_premis_modifier)
    identifier = property(get_identifier, set_identifier)
