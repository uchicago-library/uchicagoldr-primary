from re import compile as re_compile
from uuid import uuid4

from pypremis.factories import LinkingObjectIdentifierFactory
from pypremis.nodes import *

from uchicagoldrtoolsuite.core.lib.convenience import ldritem_to_premisrecord
from uchicagoldrtoolsuite.core.lib.convenience import hex_str_to_chr_str
from uchicagoldrtoolsuite.core.lib.convenience import iso8601_dt
from uchicagoldrtoolsuite.core.lib.convenience import TemporaryFilePath
from ..ldritems.abc.ldritem import LDRItem
from ..ldritems.ldrpath import LDRPath


class GenericPruner(object):
    def __init__(self, stage, patterns, exclude_patterns=None, final=False,
                 in_place_delete=False):
        self.stage = stage
        self.patterns = [re_compile(x) for x in patterns]
        if exclude_patterns is not None:
            self.exclude_patterns = [re_compile(x) for x in exclude_patterns]
        else:
            self.exclude_patterns = []
        self.final = final
        self.in_place_delete = in_place_delete

    def prune(self):
        matched_names = []
        for seg in self.stage.segment_list:
            for ms in seg.materialsuite_list:
                name_or_none = self.eval_materialsuite(
                    ms, self.patterns, self.exclude_patterns, final=self.final,
                    in_place_delete=self.in_place_delete
                )
                if name_or_none is not None:
                    matched_names.append(name_or_none)
        return matched_names

    @classmethod
    def eval_materialsuite(cls, ms, patterns, exclude_patterns=[], final=False,
                           in_place_delete=False):
        def write_premis_deletion_event(ms):
            premis_location = TemporaryFilePath()
            ms._tmp_premis_loc = premis_location

            premis = ldritem_to_premisrecord(ms.premis)
            obj = premis.get_object_list()[0]
            eventIdentifier = EventIdentifier("uuid", uuid4().hex)
            event = Event(eventIdentifier, "deletion", iso8601_dt())
            event.add_linkingObjectIdentifier(
                LinkingObjectIdentifierFactory(obj).produce_linking_node(role="deletion target")
            )
            premis.add_event(event)
            premis.write_to_file(premis_location.path)
            ms.premis = LDRPath(premis_location.path)

        def write_premis_mock_deletion_event(ms):
            premis_location = TemporaryFilePath()
            ms._tmp_premis_loc = premis_location
            premis = ldritem_to_premisrecord(ms.premis)
            obj = premis.get_object_list()[0]
            eventIdentifier = EventIdentifier("uuid", uuid4().hex)
            event = Event(eventIdentifier, "mock deletion", iso8601_dt())
            event.add_linkingObjectIdentifier(
                LinkingObjectIdentifierFactory(obj).produce_linking_node(role="mock deletion target")
            )
            premis.add_event(event)
            premis.write_to_file(premis_location.path)
            ms.premis = LDRPath(premis_location.path)

        if not isinstance(ms.premis, LDRItem):
            raise RuntimeError("All MaterialSuites must have a premis " +
                               "record before pruning can occur!")
        premis = ldritem_to_premisrecord(ms.premis)
        try:
            originalName = premis.get_object_list()[0].get_originalName()
        except KeyError:
            # theres no originalName set in the PREMIS
            # should this instead raise a RuntimeError?
            # (this probably means its a presform)
            return
        try:
            originalName = hex_str_to_chr_str(originalName)
        except:
            # The filename doesn't re-encode cleanly in utf-8
            # should this instead raise a RuntimeError?
            return

        matched = False
        for patt in patterns:
            if patt.match(originalName):
                matched = True
                break
        if matched:
            for ex_patt in exclude_patterns:
                if ex_patt.match(originalName):
                    matched = False
                    break

        if matched:
            if final is True:
                write_premis_deletion_event(ms)
                if in_place_delete is True:
                    ms.content.delete(final=final)
                del ms.content
            else:
                write_premis_mock_deletion_event(ms)
            return originalName
