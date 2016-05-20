from tempfile import TemporaryDirectory
from os.path import join
from uuid import uuid1

from pypremis.lib import PremisRecord
from pypremis.nodes import *

from .ldrpath import LDRPath
from .premisextensionnodes import Restriction
from .ldritemoperations import copy


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class GenericPREMISRestrictionSetter(object):
    """
    Ingests a Stage which already has PREMIS records in it and sets a
    restriction node in each of their records
    """
    def __init__(self, stage, restriction, reasons=None,
                 donor_stipulations=None, linkingAgentIds=None, active=True):
        """
        spawn a restriction setter

        __Args__

        1. stage (Stage): The Stage to operate on
        2. restriction (str): The restriction code to set

        __KWArgs__

        * reasons (list [of strs]): Reasons the restriction was applied
        * donor_stipulations (list [of strs]): Any donor stipulations that
            are pertinent to this restriction
        * linkingAgentIds (list [of strs]): Any linkingAgentIdentifiers that
            are relevant to this restriction
        * active (bool): Whether or not this restriction is currently active
        """
        self.stage = stage
        self.working_dir = TemporaryDirectory()
        self.working_dir_path = self.working_dir.name
        self.restriction = restriction
        self.reasons = reasons
        self.donor_stipulations = donor_stipulations
        self.linkingAgentIds = linkingAgentIds
        self.active = active

    def process(self):
        for segment in self.stage.segment_list:
            for materialsuite in segment.materialsuite_list:
                if not materialsuite.get_premis():
                    raise AttributeError("All material suites must have " +
                                         "PREMIS records in order to set " +
                                         "restrictions in them.")
                materialsuite.set_premis(
                    self.instantiate_and_set_restriction(
                        materialsuite.get_premis()
                    )
                )

    def instantiate_and_set_restriction(self, item):
        """
        do the work on the record

        __Args__

        1. item (LDRItem): The LDRItem of the standing PREMIS record

        __Returns__

        * return_item (LDRItem): The LDRItem of the updated PREMIS record
        """
        recv_file = join(self.working_dir_path, str(uuid1()))
        recv_item = LDRPath(recv_file)
        copy(item, recv_item)

        record = PremisRecord(frompath=recv_file)
        if record.get_rights_list():
            rights = record.get_rights_list()[0]
            try:
                rights_extension = rights.get_rightsExtension(0)
                rights_extension.add_to_field('Restriction',
                                              self.build_restriction_node(
                                                  self.restriction,
                                                  self.active,
                                                  self.reasons,
                                                  self.donor_stipulations,
                                                  self.linkingAgentIds
                                              )
                                              )
            except KeyError:
                rights.add_rightsExtension(build_rights_extension_node(
                    self.restriction,
                    self.active,
                    self.reasons,
                    self.donor_stipulations,
                    self.linkingagentIds
                )
                )
        else:
            rights = Rights(rightsExtension=self.build_rights_extension_node(
                self.restriction,
                self.reasons,
                self.donor_stipulations,
                self.linkingAgentIds,
                self.active
            )
            )
            record.add_rights(rights)

        new_record = join(self.working_dir_path, str(uuid1()))
        record.write_to_file(new_record)
        return_item = LDRPath(new_record)
        return return_item

    def build_rights_extension_node(self,
                                    restriction_code,
                                    restriction_reasons=None,
                                    donor_stipulations=None,
                                    linkingAgentIds=None,
                                    active=True):
        rights_extension = RightsExtension()
        rights_extension.add_to_field(
            'Restriction',
            self.build_restriction_node(
                restriction_code=restriction_code,
                restriction_reason=restriction_reasons,
                donor_stipulation=donor_stipulations,
                linkingAgentIds=linkingAgentIds,
                active=active
            )
        )
        return rights_extension

    def build_restriction_node(self,
                               restriction_code,
                               active=True,
                               restriction_reason=None,
                               donor_stipulation=None,
                               linkingAgentIds=None):
        restrictionNode = Restriction(restriction_code, active)
        if restriction_reason:
            for x in restriction_reason:
                restrictionNode.add_restrictionReason(x)
        if donor_stipulation:
            for x in donor_stipulation:
                restrictionNode.add_donorStipulation(x)
        if linkingAgentIds:
            for x in linkingAgentIds:
                restrictionNode.add_linkingAgentIdentifier(x)
        return restrictionNode
