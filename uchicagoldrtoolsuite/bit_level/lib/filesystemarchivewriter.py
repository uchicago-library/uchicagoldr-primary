
from datetime import datetime
from os import makedirs
from os.path import basename, dirname, exists, join, split
from sys import stderr
from tempfile import TemporaryFile
from xml.etree import ElementTree

from pypremis.lib import PremisRecord
from pypremis.nodes import Event, EventIdentifier,\
    EventOutcomeInformation, LinkingAgentIdentifier, LinkingObjectIdentifier,\
    LinkingEventIdentifier
from uchicagoldrtoolsuite.core.lib.idbuilder import IDBuilder

from .abc.archiveserializationwriter import ArchiveSerializationWriter
from .archive import Archive
from .archivefitsmodifier import ArchiveFitsModifier
from .archivepremismodifier import ArchivePremisModifier
from .archiveauditor import ArchiveAuditor
from .ldritemoperations import copy
from .ldrpath import LDRPath
from .pairtree import Pairtree

__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class FileSystemArchiveWriter(ArchiveSerializationWriter):
    """
    writes an archive structure to the file system as a directory
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
        self.pairtree = Pairtree(self.structure.identifier).get_pairtree_path()
        self.audit_qualification = ArchiveAuditor(origin_loc, aStructure)
        self.origin_root = split(origin_loc)[0]
        self.identifier = IDBuilder().build('premisID')
        self.premis_modifier = ArchivePremisModifier
        self.fits_modifier = ArchiveFitsModifier
        self.archive_loc = archive_loc

    def write(self):
        if self.structure.validate() and self.audit_qualification.audit():
            data_dir = join(self.archive_loc, self.pairtree, 'data')
            admin_dir = join(self.archive_loc, self.pairtree, 'admin')
            makedirs(data_dir, exist_ok=True)
            makedirs(admin_dir, exist_ok=True)
            accrecord_dir = join(admin_dir, 'accessionrecord')
            legalnote_dir = join(admin_dir, 'legalnotes')
            adminnote_dir = join(admin_dir, 'adminnotes')
            makedirs(accrecord_dir, exist_ok=True)
            makedirs(legalnote_dir, exist_ok=True)
            makedirs(adminnote_dir, exist_ok=True)
            for n_acc_record in self.structure.accessionrecord_list:
                acc_filename = basename(n_acc_record.content.item_name)
                copy(n_acc_record.content, LDRPath(
                    join(accrecord_dir,
                         acc_filename)))
            for n_legal_note in self.structure.legalnote_list:
                legalnote_filename = basename(n_legal_note.
                                              content.item_name)
                copy(n_legal_note.content, LDRPath(
                    join(legalnote_dir,
                         legalnote_filename)))
            for n_adminnote in self.structure.adminnote_list:
                adminnote_filename = basename(n_adminnote.content.
                                              item_name)
                copy(n_adminnote.content.itemB, LDRPath(
                    join(adminnote_dir,
                         adminnote_filename)))
            for n_segment in self.structure.segment_list:
                segment_id = n_segment.label+'-'+str(n_segment.run)
                techmd_dir = join(admin_dir, segment_id, 'TECHMD')
                premis_dir = join(admin_dir, segment_id, 'PREMIS')
                makedirs(
                    join(
                        admin_dir, segment_id), exist_ok=True)
                makedirs(
                    join(data_dir, segment_id), exist_ok=True)
                makedirs(
                    join(
                        premis_dir), exist_ok=True)
                makedirs(
                    join(
                        techmd_dir), exist_ok=True)

                for n_msuite in n_segment.materialsuite_list:
                    n_content_destination_fullpath = join(
                        data_dir, segment_id, n_msuite.content.item_name)
                    new_premis_record = self.premis_modifier(
                        n_msuite.premis, n_content_destination_fullpath).\
                        modify_record

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
                        data_dir, n_msuite.content.item_name)
                    new_content_ldrpath = LDRPath(new_content_path)
                    new_premis_record.write(new_premis_path)
                    copy(n_msuite.content, new_content_ldrpath)

                    for n_techmd in n_msuite.technicalmetadata_list:
                        new_tech_record_loc = join(
                            techmd_dir, n_techmd.content.item_name)
                        new_tech_record = self.fits_modifier(
                            n_techmd, new_tech_record_loc).modify_record()
                        new_tech_path = join(
                            techmd_dir, n_techmd.item_name)
                        new_tech_record.write(new_tech_path)

                    for n_presform in n_msuite.presform:
                        n_destination_fullpath = join(
                            data_dir, segment_id, n_presform.content.item_name)
                        new_premis_record = self.premis_modifier(
                            n_presform.premis, n_destination_fullpath).\
                            modify_record()
                        makedirs(
                            join(data_dir, dirname(
                                n_presform.content.item_name)), exist_ok=True)
                        makedirs(
                            join(premis_dir, dirname(
                                n_presform.content.item_name)), exist_ok=True)
                        makedirs(
                            join(techmd_dir, dirname(
                                n_presform.content.item_name)), exist_ok=True)
                        new_premis_path = join(
                            premis_dir, n_presform.premis.item_name)
                        new_presform_content_path = join(
                            data_dir, n_presform.content.item_name)
                        new_presform_content_ldrpath = LDRPath(
                            new_presform_content_path)
                        new_premis_record.write(new_premis_path)
                        copy(n_presform.content, new_presform_content_ldrpath)

                        for n_techmd in n_presform.technicalmetadata_list:
                            new_tech_record_loc = join(
                                techmd_dir, n_techmd.content.item_name)
                            new_tech_record = self.fits_modifier(
                                n_techmd, new_tech_record_loc).modify_record()
                            new_tech_path = join(
                                techmd_dir, n_techmd.item_name)
                            new_tech_record.write(new_tech_path)
        else:
            stderr.write(self.structure.explain_results())
            stderr.write(self.audit_qualification.show_errors())

    def extract_fixity_info(self, characteristics_list):
        output = []
        for characteristic in characteristics_list:
            for fixity_info in characteristic.get_fixity():
                digest_type = fixity_info.get_messageDigestAlgorithm()
                digest_value = fixity_info.get_messageDigest()
                output.append((digest_type, digest_value))
        return output

    structure = property(get_structure, set_structure)
    pairtree = property(get_pairtree, set_pairtree)
    origin_root = property(get_origin_root, set_origin_root)
    archive_loc = property(get_archive_loc, set_archive_loc)
