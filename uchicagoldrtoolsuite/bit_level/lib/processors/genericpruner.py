from uuid import uuid4

from pypremis.factories import LinkingObjectIdentifierFactory
from pypremis.nodes import *

from uchicagoldrtoolsuite.core.lib.convenience import ldritem_to_premisrecord
from uchicagoldrtoolsuite.core.lib.convenience import iso8601_dt
from uchicagoldrtoolsuite.core.lib.convenience import TemporaryFilePath
from ..ldritems.ldrpath import LDRPath


def default_callback(premis, patterns, exclude_patterns=None):
    """
    See if an originalName field matches any of a set of patterns
    and does not match any exclude patterns

    __Args__

    1. premis (PremisRecord): The PREMIS record that contains the object
        whose originalName we want to test again
    2. patterns ([re.regex]): A list of regular expressions to check

    __KWArgs__

    * exclude_patterns ([re.regex] || None): An array of patterns which
        "excuse" an originalName from a match against a pattern, or None
    """
    try:
        # Keep in mind, the originalName field is the result of calling
        # fsencode on whatever the pathname is - relative to a supplied
        # root if one is given (at least if you are using the
        # ExternalFileSystemSegmentPackager).
        originalName = premis.get_object_list()[0].get_originalName()
    except KeyError:
        # theres no originalName set in the PREMIS
        # should this instead raise a RuntimeError?
        # (this probably means its a presform)
        return

    matched = False
    for patt in patterns:
        if patt.match(originalName):
            matched = True
            break
    if matched:
        if exclude_patterns:
            for ex_patt in exclude_patterns:
                if ex_patt.match(originalName):
                    matched = False
                    break
    if matched:
        return True

class GenericPruner(object):
    """
    A class for pruning MaterialSuites out of a stage after they have been
    added to it by an ExternalPackager. Utilizes a provided callback funcion
    which operates on the MaterialSuite's PREMIS record to determine whether
    or not to prune
    """
    def __init__(self, stage, callback=default_callback, callback_args=[],
                 callback_kwargs={}, final=False, in_place_delete=False):
        """
        Create a new pruner

        __Args__

        1. stage (Stage): The stage to prune

        __KWArgs__

        * callback (callable): The callback that will be provided with the
            PremisRecord instance as well as any user supplied args/kwargs
        * callback_args (list): arguments to pass into the callback function,
            the PremisRecord instance is always the first argument regardless
            of what is passed in this array.
        * callback_kwargs (dict): kwargs to pass into the callback function
        * final (bool): Whether or not take _any_ real actions, or only
            mock actions recorded in the PREMIS
        * in_place_delete (bool): If True && final --> fire the LDRItem.delete()
            method on the content of MaterialSuites matched by the callback
        """
        self.stage = stage
        self.final = final
        self.in_place_delete = in_place_delete
        self.callback = callback
        self.callback_args = callback_args
        self.callback_kwargs = callback_kwargs

    def prune(self, callback=None, callback_args=None, callback_kwargs=None,
              final=None, in_place_delete=None):
        """
        Prunes the provided stage. All arguments default to values provided
            to the instance on init

        __KWArgs__

        * callback (callable): The callback that will be provided with the
            PremisRecord instance as well as any user supplied args/kwargs
        * callback_args (list): arguments to pass into the callback function,
            the PremisRecord instance is always the first argument regardless
            of what is passed in this array.
        * callback_kwargs (dict): kwargs to pass into the callback function
        * final (bool): Whether or not take _any_ real actions, or only
            mock actions recorded in the PREMIS
        * in_place_delete (bool): If True && final --> fire the LDRItem.delete()
            method on the content of MaterialSuites matched by the callback

        __Returns__

        matched_identifiers ([str]): The identifiers of all matched
            MaterialSuites
        """
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

        if callback is None:
            callback = self.callback
        if callback_args is None:
            callback_args = self.callback_args
        if callback_kwargs is None:
            callback_kwargs = self.callback_kwargs
        if final is None:
            final = self.final
        if in_place_delete is None:
            in_place_delete = self.in_place_delete

        matched_identifiers = []
        for seg in self.stage.segment_list:
            for ms in seg.materialsuite_list:
                premis = ldritem_to_premisrecord(ms.premis)
                identifier = premis.get_object_list()[0].get_objectIdentifier()[0].get_objectIdentifierValue()
                if callback(premis, *callback_args, **callback_kwargs) is True:
                    matched_identifiers.append(identifier)
                    if final is True:
                        if self.in_place_delete is True:
                            ms.content.delete(final=True)
                        del ms.content
                        write_premis_deletion_event(ms)
                    else:
                        write_premis_mock_deletion_event(ms)
        return matched_identifiers
