from re import compile as re_compile

class GenericPruner(object):
    def __init__(self, stage, patterns, exclude_patterns=None, final=False):
        self.stage = stage
        self.patterns = [re_compile(x) for x in patterns]
        if exclude_patterns is not None:
            self.exclude_patterns = [re_compile(x) for x in exclude_patterns]
        else:
            self.exclude_patterns = []
        self.final = final

    def prune(self):
        report = {}
        for seg in self.stage.segment_list:
            to_delete = []
            for ms in seg.materialsuite_list:
                if ms.presform_list:
                    raise RuntimeError("the pruner can not operate on " +
                                       "stages for which presforms have " +
                                       "been generated.")
                if ms.premis:
                    raise RuntimeError("the pruner can not operate on " +
                                       "stages for which PREMIS has " +
                                       "been generated.")
                if ms.technicalmetadata_list:
                    raise RuntimeError("the pruner can not operate on " +
                                       "stages for which techmd has " +
                                       "been generated.")
                if self._check_match(ms.content.item_name):
                    to_delete.append(ms.content)
            for x in to_delete:
                report_identifier = "{}|{}".format(
                    seg.identifier, x.item_name
                )
                if self.final is True:
                    try:
                        x.delete(final=self.final)
                        report[report_identifier] = "Deleted"
                    except:
                        report[report_identifier] = "Deletion Error"
                else:
                    report[report_identifier] = "Would have been deleted"
        return report

    def _check_match(self, x):
        for p in self.patterns:
            if p.match(x):
                excluded = False
                for ep in self.exclude_patterns:
                    if ep.match(x):
                        excluded = True
                        break
                if not excluded:
                    return True
        return False

