
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

    def run_func_on_premis(self, premis_file, a_func, data={}):
        with premis_file.open('rb') as reading_file:
            with TemporaryFile() as writing_file:
                while True:
                    buf = reading_file.read(1024)
                    if buf:
                        writing_file.write(buf)
                    else:
                        break
                writing_file.seek(0)
                premis_obj = PremisRecord(
                    frompath=writing_file)
                return a_func(premis_obj, data)

    def write_new_techmd_file(self, segment_id, a_file_object):
        new_techmd_filename = basename(
            a_file_object.item_name)
        new_techmd_path = join(
            self.archive_loc, self.pairtree, 'data',
            segment_id,
            dirname(a_file_object.item_name))
        makedirs(new_techmd_path, exist_ok=True)

        with TemporaryFile() as tempfile:
            with a_file_object.open('rb') as read_file:
                while True:
                    buf = read_file.read(1024)
                    if buf:
                        tempfile.write(buf)
                tempfile.seek(0)
                techrecord = ElementTree.parse(tempfile)
                techrecord_root = techrecord.getroot()
                filepath_node = techrecord_root.find(
                    "{http://hul.harvard.edu/ois/xml/ns/fits/" +
                    "fits_output}fileInfo/" +
                    "{http://hul.harvard.edu/ois/xml/ns/fits/" +
                    "fits_output}filePath")
                filepath_node.text = join(
                    techmd_path, techmd_filename)
                new_techmd_file = LDRPath(join(techmd_path, techmd_filename))

    def write(self):
        """
        serializes a staging directory structure into an archive structure
        onto disk
        """
        if self.structure.validate():
            audit_result = self.audit_qualification.audit()
            if audit_result:
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
                    segment_id = n_segment.label+str(n_segment.run)
                    display_segment_id = n_segment.label+'-'+str(
                        n_segment.run)
                    makedirs(join(admin_dir, segment_id), exist_ok=True)
                    makedirs(join(data_dir, segment_id), exist_ok=True)
                    makedirs(join(admin_dir, segment_id, 'PREMIS'),
                             exist_ok=True)
                    makedirs(join(admin_dir, segment_id, 'TECHMD'),
                             exist_ok=True)
                    for n_msuite in n_segment.materialsuite_list:
                        main_output = self.run_func_on_premis(
                            n_msuite.premis,
                            self.extract_record_info,
                            {'segment': display_segment_id}
                        )
                        new_record = self.run_func_on_premis(
                            n_msuite.premis,
                            self.modify_record_location_value,
                            {'segment': display_segment_id,
                             'path_tail': n_msuite.content.item_name}
                        )
                        new_record = self.run_func_on_premis(
                            n_msuite.premis,
                            self.add_new_event,
                            {'segment': display_segment_id,
                             'path_tail': n_msuite.content.item_name})

                        if getattr(n_msuite, 'technicalmetadata_list', None):
                            for n_techmd in n_msuite.technicalmetadata_list:
                                self.modify_technical_metadata(n_techmd)


                        base_premis_directory = join(
                            self.archive_loc,
                            self.pairtree,
                            'admin', display_segment_id,
                            'PREMIS', dirname(n_msuite.content.item_name))
                        makedirs(base_premis_directory, exist_ok=True)
                        new_record.write_to_file(join(
                            self.archive_loc,
                            self.pairtree, 'admin',
                            display_segment_id, 'PREMIS',
                            n_msuite.premis.item_name))
                        if getattr(n_msuite, 'presform_list', None):
                            for n_presform in n_msuite.presform_list:
                                cur_output = self.run_func_on_premis(
                                    n_presform.premis,
                                    self.extract_record_info,
                                    {'segment': display_segment_id}
                                )
                                cur_new_record = self.run_func_on_premis(
                                    n_msuite.premis,
                                    display_segment_id,
                                    self.modify_record_location_value,
                                    {'segment': display_segment_id,
                                     'path_tail': n_presform.content.item_name}
                                )
                                cur_new_record.write(
                                    join(self.pairtree,
                                         'admin',
                                         display_segment_id,
                                         n_presform.premis.item_name)
                                )

                        manifest_line = "{}".format(
                            join(self.pairtree, 'data', display_segment_id,
                                 n_msuite.content.item_name))
                        for m_bit in main_output:
                            manifest_line += "\t{}".format(m_bit)
                        manifest_line += "\n"
                        manifest_line = manifest_line.encode('utf-8')
                        manifest_line = bytes(manifest_line)
                        manifest_file = LDRPath(
                            join(self.archive_loc, 'queue.txt'))

                        with manifest_file.open('ab') as writing_file:
                            writing_file.write(manifest_line)
                        destination_dir = join(
                            self.archive_loc, self.pairtree,
                            'data', display_segment_id,
                            dirname(n_msuite.content.item_name))
                        makedirs(destination_dir, exist_ok=True)
                        destination = LDRPath(
                            join(
                                self.archive_loc, self.pairtree,
                                'data', display_segment_id,
                                n_msuite.content.item_name)
                        )

                        copy(n_msuite.content, destination, False)
            else:
                for n_message in self.audit_qualification.show_errors():
                    print("{}\n".format(n_message))
        else:
            stderr.write("invalid Archive structure instance passed" +
                         " to FileSystemArchiveWriter")

        #     for n_segment in self.structure.segment_list:
        #         segment_id = n_segment.label+str(n_segment.run)

        #         makedirs(join(admin_dir, segment_id), exist_ok=True)
        #         makedirs(join(data_dir, segment_id), exist_ok=True)
        #         makedirs(join(admin_dir, segment_id, 'premis'), exist_ok=True)
        #         makedirs(join(admin_dir, segment_id, 'techmd'), exist_ok=True)

        #         for n_msuite in n_segment.materialsuite_list:
        #             self.find_and_pairtree_data_content(
        #                 segment_id, n_msuite.content)
        #             self.find_and_pairtree_admin_content(
        #                 segment_id, 'techmd', n_msuite.technicalmetadata_list)
        #             cur_premis_filename = join(
        #                 admin_dir,
        #                 segment_id, 'premis',
        #                 basename(n_msuite.premis.item_name))
        #             cur_premis_ldrpath = LDRPath(cur_premis_filename)
        #             copy(n_msuite.premis, cur_premis_ldrpath, False)

        #             if n_msuite.presform_list:
        #                 for n_presform_msuite in n_msuite.presform_list:
        #                     self.find_and_pairtree_data_content(
        #                         segment_id, n_presform_msuite.content)
        #                     self.find_and_pairtree_admin_content(
        #                         segment_id, 'techmd',
        #                         n_presform_msuite.technicalmetadata_list)
        #                     this_premis_filename = join(
        #                         admin_dir,
        #                         segment_id, 'premis',
        #                         basename(
        #                             n_presform_msuite.premis.item_name))
        #                     this_premis_filename = LDRPath(
        #                         this_premis_filename)
        #                     copy(n_presform_msuite.premis,
        #                          this_premis_filename, False)

        #             else:
        #                 stderr.write("no presform files found\n")
        # else:
        #     stderr.write("invalid archive structure instance passed to  the " +
        #                  " file system archive structure writer")

    def get_structure(self):
        return self._structure

    def set_structure(self, value):
        if isinstance(value, Archive):
            self._structure = value
        else:
            raise ValueError("must pass an instance of Structure" +
                             " abstract class to a " +
                             "FileSystemArchiveStructureWriter")

    def get_archive_loc(self):
        return self._archive_loc

    def set_archive_loc(self, value):
        if exists(value):
            self._archive_loc = value

        else:
            raise ValueError("Cannot pass {} to the archive".format(value) +
                             " writer because that path does not exist")

    def get_pairtree(self):
        return self._pairtree

    def set_pairtree(self, value):
        self._pairtree = value

    def get_origin_root(self):
        return self._origin_root

    def set_origin_root(self, value):
        if not exists(value):
            raise ValueError("origin_root {}".format(self.origin_root) +
                             " in FileSystemArchiveWriter" +
                             " must exist on the file system")
        self._origin_root = value

    structure = property(get_structure, set_structure)
    pairtree = property(get_pairtree, set_pairtree)
    origin_root = property(get_origin_root, set_origin_root)
    archive_loc = property(get_archive_loc, set_archive_loc)
