from os import listdir
from os.path import splitext, join, basename
from uuid import uuid1()

from ...core.lib.bash_cmd import BashCommand
from .abc.converter import Converter
from .materialsuite import MaterialSuite


class OfficeToPDFConverter(Converter):

    _claimed_mimes = [
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
    libre_office_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"

    def __init__(self, target_path, target_premis_path, working_dir=None,
                 timeout=None):
        super().__init__(target_path, target_premis_path,
                         working_dir=working_dir, timeout=timeout)

    def convert(self):
        resulting_materialsuites = []

        outdir = join(self.working_dir, uuid1())
        cmd_out = []
        convert_cmd_args = [self.libre_office_path, '--headless',
                            '--convert-to', 'pdf' '--outdir', outdir,
                            self.target_path]
        convert_cmd = BashCommand(convert_cmd_args)
        convert_cmd.set_timeout(self.timeout)
        convert_cmd.run_command()
        cmd_out.append(convert_cmd.get_data())
        try:
            where_it_is = listdir(outdir)[0]
        except:
            where_it_is = None
        if where_it_is is not None:
            where_it_should_be = join(self.working_dir, self.target_path+".presform.pdf")
            mv_cmd_args = ['mv', where_it_is, where_it_should_be]
            print(mv_cmd_args)
            mv_cmd = BashCommand(mv_cmd_args)
            mv_cmd.set_timeout(self.timeout)
            mv_cmd.run_command()
            cmd_out.append(mv_cmd.get_data())
            presform_ldrpath = LDRPath(where_it_is)
            presform_ms = MaterialSuite()
            presform_ms.add_content(presform_ldrpath)
            resulting_materialsuites.append(presform_ms)
        return (resulting_materialsuites, self.target_premis_path)
