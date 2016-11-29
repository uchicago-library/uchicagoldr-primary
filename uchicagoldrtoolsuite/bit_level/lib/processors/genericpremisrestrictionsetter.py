from tempfile import TemporaryDirectory
from json import dumps
from os.path import join
from uuid import uuid1
from logging import getLogger

from pypremis.lib import PremisRecord
from pypremis.nodes import *

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.idbuilder import IDBuilder
from ..ldritems.ldrpath import LDRPath
from ..misc.premisextensionnodes import Restriction
from ..misc.premisextensionnodes import RightsExtensionIdentifier
from ..misc.premisextensionnodes import RestrictedObjectIdentifier
from ..misc.premisextensionnodes import RestrictingAgentIdentifier
from ..ldritems.ldritemcopier import LDRItemCopier
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, log_init_success


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class GenericPREMISRestrictionSetter(object):
    """
    Ingests a Stage which already has PREMIS records in it and sets a
    restriction node in each of their records
    """
    @log_aware(log)
    def __init__(self, stage, restriction, reasons=None,
                 donor_stipulations=None, restrictingAgentIds=None,
                 active=True):
        """
        spawn a restriction setter

        __Args__

        1. stage (Stage): The Stage to operate on
        2. restriction (str): The restriction code to set

        __KWArgs__

        * reasons (list [of strs]): Reasons the restriction was applied
        * donor_stipulations (list [of strs]): Any donor stipulations that
            are pertinent to this restriction
        * restrictingAgentIds (list [of strs]): Any linkingAgentIdentifiers that
            are relevant to this restriction
        * active (bool): Whether or not this restriction is currently active
        """
        log_init_attempt(self, log, locals())
        self.stage = stage
        self.working_dir = TemporaryDirectory()
        self.working_dir_path = self.working_dir.name
        self.restriction = restriction
        self.reasons = reasons
        self.donor_stipulations = donor_stipulations
        self.restrictingAgentIds = restrictingAgentIds
        self.active = active
        log_init_success(self, log)

    @log_aware(log)
    def __repr__(self):
        attr_dict = {
            'stage': str(self.stage),
            'working_dir_path': self.working_dir_path,
            'restriction': self.restriction,
            'active': self.active
        }

        if self.reasons:
            attr_dict['reasons'] = self.reasons
        else:
            attr_dict['reasons'] = None
        if self.donor_stipulations:
            attr_dict['donor_stipulations'] = self.donor_stipulations
        else:
            attr_dict['donor_stipulations'] = None
        if self.restrictingAgentIds:
            attr_dict['restricting_agent_ids'] = self.restrictingAgentIds
        else:
            attr_dict['restricting_agent_ids'] = None

        return "<GenericPREMISRestrictionSetter {}>".format(
            dumps(attr_dict, sort_keys=True))

    @log_aware(log)
    def process(self):
        log.debug("Beginning PREMIS restriction setting.")
        s_num = 0
        for segment in self.stage.segment_list:
            s_num += 1
            ms_num = 0
            for materialsuite in segment.materialsuite_list:
                ms_num += 1
                log.debug(
                    "Processing Segment {}/{}, MaterialSuite {}/{}".format(
                        str(s_num), str(len(self.stage.segment_list)),
                        str(ms_num), str(len(segment.materialsuite_list))
                    )
                )
                if not materialsuite.get_premis():
                    raise AttributeError("All material suites must have " +
                                         "PREMIS records in order to set " +
                                         "restrictions in them.")
                log.debug(
                    "Setting restriction in PREMIS for {}.".format(
                        materialsuite.identifier
                    )
                )
                materialsuite.set_premis(
                    self.instantiate_and_set_restriction(
                        materialsuite.get_premis()
                    )
                )

    @log_aware(log)
    def instantiate_and_set_restriction(self, item):
        """
        do the work on the record

        __Args__

        1. item (LDRItem): The LDRItem of the standing PREMIS record

        __Returns__

        * return_item (LDRItem): The LDRItem of the updated PREMIS record
        """
        log.debug("Temporarily instantiating PREMIS file")
        recv_file = join(self.working_dir_path, str(uuid1()))
        recv_item = LDRPath(recv_file)
        c = LDRItemCopier(item, recv_item)
        c.copy()

        log.debug("Parsing existing PREMIS")
        record = PremisRecord(frompath=recv_file)

        # Pull the object id out here
        obj_to_link = record.get_object_list()[0]

        log.debug("Inserting restriction elements.")
        if record.get_rights_list():
            rights = record.get_rights_list()[0]
            rights.add_rightsExtension(
                self.build_rights_extension_node(
                    self.restriction,
                    obj_to_link,
                    self.active,
                    self.reasons,
                    self.donor_stipulations,
                    self.restrictingAgentIds
                )
            )
        else:
            rights = Rights(rightsExtension=self.build_rights_extension_node(
                self.restriction,
                obj_to_link,
                self.active,
                self.reasons,
                self.donor_stipulations,
                self.restrictingAgentIds
            )
            )
            record.add_rights(rights)

        new_record = join(self.working_dir_path, str(uuid1()))
        record.write_to_file(new_record)
        return_item = LDRPath(new_record)
        return return_item

    @log_aware(log)
    def build_rights_extension_node(self,
                                    restriction_code,
                                    obj_to_link,
                                    active=True,
                                    restriction_reasons=None,
                                    donor_stipulations=None,
                                    restrictingAgentIds=None):
        rights_extension = RightsExtension()

        rights_extension.set_field(
            'rightsExtensionIdentifier',
            self.build_rightsExtensionIdentifier()
        )

        rights_extension.set_field(
            'restriction',
            self.build_restriction_node(
                restriction_code,
                obj_to_link,
                active=active,
                restriction_reason=restriction_reasons,
                donor_stipulation=donor_stipulations,
                restrictingAgentIds=restrictingAgentIds,
            )
        )
        return rights_extension

    @log_aware(log)
    def build_rightsExtensionIdentifier(self):
        idb = IDBuilder()
        id_tup = idb.build("premisID").show()
        return RightsExtensionIdentifier(id_tup[0], id_tup[1])

    @log_aware(log)
    def build_restrictingAgentIdentifier(self):
        idb = IDBuilder()
        id_tup = idb.build("premisID").show()
        return RestrictingAgentIdentifier(id_tup[0], id_tup[1])

    @log_aware(log)
    def build_restriction_node(self,
                               restriction_code,
                               obj_to_link,
                               active=True,
                               restriction_reason=None,
                               donor_stipulation=None,
                               restrictingAgentIds=None):

        restrictedObjectIdentifier = \
            self.build_restrictedObjectIdentifierFromObj(obj_to_link)

        restrictionNode = Restriction(restriction_code, str(active),
                                      restrictedObjectIdentifier)
        if restriction_reason:
            for x in restriction_reason:
                restrictionNode.add_restrictionReason(x)
        if donor_stipulation:
            for x in donor_stipulation:
                restrictionNode.add_donorStipulation(x)
        if restrictingAgentIds:
            for x in restrictingAgentIds:
                restrictionNode.add_restrictingAgentIdentifier(x)
        return restrictionNode

    @log_aware(log)
    def build_restrictedObjectIdentifierFromObj(self, obj_to_link):
        objIDType = \
            obj_to_link.get_objectIdentifier(0).get_objectIdentifierType()
        objIDValue = \
            obj_to_link.get_objectIdentifier(0).get_objectIdentifierValue()
        restrictedObjectIdentifier = RestrictedObjectIdentifier(
            objIDType,
            objIDValue
        )
        return restrictedObjectIdentifier
