
from os import makedirs
from os.path import basename, dirname, exists, join, split
from sys import stderr
from tempfile import TemporaryFile

from pypremis.lib import PremisRecord

from .abc.archiveserializationwriter import ArchiveSerializationWriter
from .archive import Archive
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
        self.archive_loc = archive_loc

    def pairtree_an_admin_content(self, type_str, segment_id, a_thing):
        return LDRPath(join(self.archive_loc, self.pairtree,
                            'admin', type_str, segment_id, a_thing.item_name))

    def pairtree_a_data_content(self, segment_id, a_thing):
        return LDRPath(join(self.archive_loc, self.pairtree,
                            'data', segment_id, a_thing.item_name))

    def find_and_pairtree_admin_content(self, segment_id, type_str,
                                        iterable):
        if iterable:
            for n_thing in iterable:
                makedirs(join(self.archive_loc, self.pairtree,
                              'admin', type_str, segment_id,
                              dirname(n_thing.item_name)),
                         exist_ok=True)
                n_thing_destination = self.pairtree_an_admin_content(
                    type_str, segment_id,
                    n_thing)
                copy(n_thing, n_thing_destination, False)
        else:
            stderr.write("nothing found\n")

    def find_and_pairtree_data_content(self, segment_id, n_thing):
        makedirs(join(self.archive_loc, self.pairtree,
                      'data', segment_id, dirname(n_thing.item_name)),
                 exist_ok=True)
        n_thing_destination = self.pairtree_a_data_content(segment_id,
                                                           n_thing)
        copy(n_thing, n_thing_destination, False)

    def write(self):
        """
        serializes a staging directory structure into an archive structure
        onto disk
        """
        if self.structure.validate():
            audit_result = self.audit_qualification.audit()
            if audit_result[0]:
                data_dir = join(self.archive_loc, self.pairtree, 'data')
                admin_dir = join(self.archive_loc, self.pairtree, 'admin')
                print(data_dir)
                print(admin_dir)
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
                    makedirs(join(admin_dir, segment_id), exist_ok=True)
                    makedirs(join(data_dir, segment_id), exist_ok=True)
                    makedirs(join(admin_dir, segment_id, 'PREMIS'),
                             exist_ok=True)
                    makedirs(join(admin_dir, segment_id, 'TECHMD'),
                             exist_ok=True)

                    for n_msuite in n_segment.materialsuite_list:
                        new_filename = ""
                        with n_msuite.premis.open('rb') as reading_file:
                            with TemporaryFile() as writing_file:
                                while True:
                                    buf = reading_file.read(1024)
                                    if buf:
                                        writing_file.write(buf)
                                    else:
                                        break
                                writing_file.seek(0)
                                manifest_line = []
                                precord = PremisRecord(
                                    frompath=writing_file)
                                for obj in precord.get_object_list():
                                    for storage in obj.get_storage():
                                        if not storage.get_contentLocation():
                                            self.errors.add(
                                                "premis",
                                                "no contentLocation " +
                                                "element found")
                                        else:
                                            old_location = storage.get_contentLocation()
                                            display_segment_id = n_segment.label+str(n_segment.run)
                                            new_location = join(self.pairtree, 'data', n_msuite.content.item_name)
                                            old_location.set_contentLocationValue(new_location)
                                            print(storage.get_contentLocation().get_contentLocationValue())

                                            manifest_line.append(new_location)

                                    for characteristic in obj.get_objectCharacteristics():
                                        for fixity in characteristic.get_fixity():
                                            digest_type = fixity.get_messageDigestAlgorithm()
                                            digest_string = fixity.get_messageDigest()

                                            manifest_line.append(
                                                (digest_type,
                                                 digest_string))
                                    print(manifest_line)

                        if getattr(n_msuite, 'presform_list', None):
                            for n_presform in n_msuite.presform_list:
                                with n_msuite.premis.open('rb') \
                                     as reading_file:
                                    with TemporaryFile() as writing_file:
                                        while True:
                                            buf = reading_file.read(1024)
                                    if buf:
                                        writing_file.write(buf)
                                    else:
                                        break
                                    writing_file.seek(0)
                                    precord = PremisRecord(
                                        frompath=writing_file)
                                    print(precord)
                                print(n_presform.premis)

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
