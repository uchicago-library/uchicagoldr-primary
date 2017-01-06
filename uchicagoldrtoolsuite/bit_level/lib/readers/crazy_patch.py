from pathlib import Path

from pypremis.lib import PremisRecord

from uchicagoldrtoolsuite.core.lib.convenience import recursive_scandir
from uchicagoldrtoolsuite.bit_level.lib.structures.stage import Stage
from uchicagoldrtoolsuite.bit_level.lib.structures.materialsuite import MaterialSuite
from uchicagoldrtoolsuite.bit_level.lib.ldritems.ldrpath import LDRPath


class CrazyReader:
    """
    Reads the old Stage serialization, disregarding presforms and techmd
    (presforms don't exist for any of the stages that need porting, techmd
    is being disregarded if it does) and packs them into new-form stages,
    in theory ready for transformation and serialization into LTS
    """
    def __init__(self, staging_env, identifier):
        self.path = Path(staging_env, identifier)

    def read(self):
        data_dir = Path(self.path, 'data')
        admin_dir = Path(self.path, 'admin')

        identifier = self.path.parts[-1]

        stage = Stage(identifier)

        accessionrecords_dir = Path(admin_dir, 'accessionrecords')
        adminnotes_dir = Path(admin_dir, 'adminnotes')
        legalnotes_dir = Path(admin_dir, 'legalnotes')

        for x in recursive_scandir(str(accessionrecords_dir)):
            if not x.is_file():
                continue
            stage.add_accessionrecord(LDRPath(x.path))

        for x in recursive_scandir(str(adminnotes_dir)):
            if not x.is_file():
                continue
            stage.add_adminnote(LDRPath(x.path))

        for x in recursive_scandir(str(legalnotes_dir)):
            if not x.is_file():
                continue
            stage.add_legalnote(LDRPath(x.path))

        for x in recursive_scandir(str(data_dir)):
            if not x.is_file():
                continue
            path = Path(x.path)
            rel_path = path.relative_to(data_dir)
            segment = rel_path.parts[0]
            premis_path = Path(self.path, 'admin', segment, 'PREMIS', *rel_path.parts[1:])
            premis_path = Path(str(premis_path)+'.premis.xml')
            assert(premis_path.exists())
            premis = PremisRecord(frompath=str(premis_path))
            ms_identifier = premis.get_object_list()[0].get_objectIdentifier()[0].get_objectIdentifierValue()
            ms = MaterialSuite(ms_identifier)
            ms.content = LDRPath(x.path)
            ms.premis = LDRPath(str(premis_path))
            stage.add_materialsuite(ms)

        return stage
