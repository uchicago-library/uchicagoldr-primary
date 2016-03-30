class Pruner(FileProcessor):
    pattern_inputs = []
    patterns_compiled = []
    def __init__(self, directory, source_root, patterns):
        FileProcessor.__init__(self, directory, source_root, irrelevant_part = source_root)
        self.pattern_inputs = patterns

    def validate(self):
        for n in self.pattern_inputs:
            current_n = re_compile(n)
            if len(self.pattern_matching_files_regex(current_n)) == 0:
                return False
        return True

    def explain_validation_result(self):
        for n in self.pattern_inputs:
            current_n = re_compile(n)
            if len(self.pattern_matching_files_regex(current_n)):
                return namedtuple("problem" "category message") \
                    ("fatal",
                     "The pattern {} does not match any files in the directory.".format(n))
        return namedtuple("problem", "category message") \
            ("non-fatal", "something something")

    def ingest(self):
        count = 0
        for n in self.pattern_inputs:
            current_n = re_compile(n)
            matches = self.pattern_matching_files_regex(current_n)
            for m in matches:
                os.remove(m.data.filepath)
                count += 1
        return count
