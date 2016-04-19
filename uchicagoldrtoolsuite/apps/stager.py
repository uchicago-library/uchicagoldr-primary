from os.path import join
from uchicagoldrtoolsuite.apps.internals.cliapp import CLIApp
from uchicagoldrtoolsuite.lib.structuring.stagingdirectoryreader import StagingDirectoryReader
from uchicagoldrtoolsuite.lib.structuring.stagingdirectorywriter import StagingDirectoryWriter
from uchicagoldrtoolsuite.lib.structuring.stagingdirectorywriter import StagingDirectoryWriter

__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


def launch():
    app = Stager(
            __author__=__author__,
            __email__=__email__,
            __company__=__company__,
            __copyright__=__copyright__,
            __publication__=__publication__,
            __version__=__version__
    )
    app.main()


class Stager(CLIApp):
    def main(self):
        # Instantiate boilerplate parser
        self.spawn_parser(description="The UChicago LDR Tool Suite utility " +
                          "for moving materials into staging structures.",
                          epilog="{}\n".format(self.__copyright__) +
                          "{}\n".format(self.__author__) +
                          "{}".format(self.__email__))
        # Add application specific flags/arguments
        self.parser.add_argument("--resume", "-r", help="An integer for a " +
                                 "run that needs to be resumed.",
                                 type=int, action='store', default=0)
        self.parser.add_argument("--group", "-g", help="The name of a group " +
                                 "to assign group ownership to the new " +
                                 "staging directory",
                                 type=str, action='store', default='None')
        self.parser.add_argument("directory", help="The directory that needs " +
                                 "to be staged.",
                                 type=str, action='store')
        self.parser.add_argument("numfiles", help="The number of files that " +
                                 "you are expecting to process",
                                 type=int, action='store')
        self.parser.add_argument("source_root", help="The root of the  " +
                                 "directory that needs to be staged.",
                                 type=str, action='store')
        self.parser.add_argument("destination_root", help="The location that " +
                                 "the staging directory should be created in",
                                 type=str, action='store')
        self.parser.add_argument("staging_id", help="The identifying name " +
                                 "for the new staging directory",
                                 type=str, action='store')
        self.parser.add_argument("prefix", help="The prefix defining the " +
                                 "type of run that is being processed",
                                 type=str, action='store')

        # Parse arguments into args namespace
        args = self.parser.parse_args()
        
        # App code
        
        staging_directory = join(args.destination_root, args.staging_id)
        staging_directory_reader = StagingDirectoryReader(staging_directory)
        staging_structure = staging_directory_reader.read()
        segment_packger = SegmentPackager(a_directory, prefix, number=0)
        new_segment = segment_packager.create_segment()
        print(new_segment)
        

    # def add_to_structure(self, a_directory, prefix, source_root='', number=0):
    #     tree = AbsoluteFilePathTree(a_directory)
    #     just_files = tree.get_files()
    #     all_nodes = tree.get_nodes()
    #     just_directories = [x.identifier for x in all_nodes
    #                             if x.identifier not in just_files]
    #     last_segments = self.structure.segment
    #     pattern_match = re.compile('(\w{1,})(\d{1,})')
    #     potential_past_relevant_segments = []
    #     for n_segment in last_segments:
    #         print(n_segment)
    #         pattern_match_group = pattern_match.match(n_segment.identifier)
    #         n_prefix, n_number = pattern_match_group.group(1), int(pattern_match_group.group(2))
    #         if n_number == number:
    #             data_node_depth = tree.find_depth_of_a_pa)

    #         if n_prefix == prefix:
    #             potential_past_relevant_segments.append(n_segment)

    #     potential_past_relevant_segments.sort(key=lambda x: x.identifier)
    #     if len(potential_past_relevant_segments) > 0:
    #         last_segment = potential_past_relevant_segments[-1]
    #         current_segment_id = str(int(pattern_match.match(last_segment.identifier).\
    #                                       group(2))+1)
    #     else:
    #         current_segment_id = '1'
    #     newsegment = SegmentStructure(prefix, current_segment_id)
    #     for n_thing in just_directories:
    #         a_file = LDRPathRegularDirectory(n_thing)
    #         msuite = MaterialSuiteStructure(a_file.item_name)
    #         msuite.original.append(a_file)
    #         newsegment.materialsuite.append(msuite)
    #     for n_thing in just_files:
    #         a_file = LDRPathRegularFile(n_thing)
    #         msuite = MaterialSuiteStructure(a_file.item_name)
    #         msuite.original.append(a_file)
    #         newsegment.materialsuite.append(msuite)
    #     self.structure.segment.append(newsegment)      
        
        
        stagingwriter = staging_directory_reader.add_to_structure(args.directory, args.prefix,
                                                                  source_root=args.source_root,
                                                                  number=args.resume)
        # stagingwriter.write()
        
if __name__ == "__main__":
    s = Stager()
    s.main()
