from pypremis.nodes import ExtensionNode
from controlledvocab.lib import ControlledVocabulary as CV


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class linkingRightsExtensionIdentifier(ExtensionNode):
    def __init__(self, linkingRightsExtensionIdentifierType,
                 linkingRightsExtensionIdentifierValue,
                 linkingRightsExtensionIdentifierRole=None):

        ExtensionNode.__init__(self)
        self.set_linkingRightsExtensionIdentifierType(
            linkingRightsExtensionIdentifierType
        )
        self.set_linkingRightsExtensionIdentifierValue(
            linkingRightsExtensionIdentifierValue
        )
        if linkingRightsExtensionIdentifierRole is not None:
            self.set_linkingRightsExtensionIdentifierRole(
                linkingRightsExtensionIdentifierRole
            )

    def set_linkingRightsExtensionIdentifierType(self, linkingRightsExtensionIdentifierType):
        self.set_field('linkingRightsExtensionIdentifierType', linkingRightsExtensionIdentifierType)

    def get_linkingRightsExtensionIdentifierType(self):
        return self.get_field('linkingRightsExtensionIdentifierType')

    def set_linkingRightsExtensionIdentifierValue(self, linkingRightsExtensionIdentifierValue):
        self.set_field('linkingRightsExtensionIdentifierValue', linkingRightsExtensionIdentifierValue)

    def get_linkingRightsExtensionIdentifierValue(self):
        return self.get_field('linkingRightsExtensionIdentifierValue')

    def set_linkingRightsExtensionIdentifierRole(self, linkingRightsExtensionIdentifierRole):
        self.set_field('linkingRightsExtensionIdentifierRole', linkingRightsExtensionIdentifierRole)

    def add_linkingRightsExtensionIdentifierRole(self, linkingRightsExtensionIdentifierRole):
        self.add_to_field('linkingRightsExtensionIdentifierRole', linkingRightsExtensionIdentifierRole)

    def get_linkingRightsExtensionIdentifierRole(self):
        return self.get_field('linkingRightsExtensionIdentifierRole')


class RightsExtensionIdentifier(ExtensionNode):
    """
    A node to meant to mimic the rightsStatementIdentifier node
    ...
    but for rightsExtension nodes
    """
    def __init__(self, rightsExtensionIdentifierType,
                 rightsExtensionIdentifierValue):
        ExtensionNode.__init__(self)
        self.set_rightsExtensionIdentifierType(rightsExtensionIdentifierType)
        self.set_rightsExtensionIdentifierValue(rightsExtensionIdentifierValue)

    def set_rightsExtensionIdentifierType(self, rightsExtensionIdentifierType):
        self.set_field('rightsExtensionIdentifierType', rightsExtensionIdentifierType)

    def get_rightsExtensionIdentifierType(self):
        return self.get_field('rightsExtensionIdentifierType')

    def set_rightsExtensionIdentifierValue(self, rightsExtensionIdentifierValue):
        self.set_field('rightsExtensionIdentifierValue', rightsExtensionIdentifierValue)

    def get_rightsExtensionIdentifierValue(self):
        return self.get_field('rightsExtensionIdentifierValue')


class Restriction(ExtensionNode):
    """
    A restriction node for use in PREMIS records describing LDR Items
    """

    restriction_codes_strs = [
        "O",
        "OU",
        "R-DA",
        "R-30",
        "R-50",
        "R-80",
        "R-X",
        "R-P30",
        "R-S"
        ]

    restriction_code_patterns = [
        "^DR-[0-9]+$",
        "^OO-[0-9]{2}/[0-9]{2}/[0-9]{4}$",
        "^R-[0-9]+D$",
        "^MR-.+$"
        ]

    restriction_code_cv = CV(contains=restriction_codes_strs,
                             patterns=restriction_code_patterns)

    def __init__(self, restrictionCode, active, linkingObjectIdentifier):
        """
        create a minimal restriction node

        __Args__

        1. restrictionCode (str): A restriction code
        2. active (str||bool): "True" or "False" to denote whether
        the restriction is active
        """
        ExtensionNode.__init__(self)
        self.set_restrictionCode(restrictionCode)
        self.set_active(active)
        self.set_linkingObjectIdentifier(linkingObjectIdentifier)

    def set_restrictionCode(self, restrictionCode):
        """
        set the instances restriction code

        __Args__

        1. restrictionCode(str): a restriction code
        """
        if restrictionCode not in self.restriction_code_cv:
            raise ValueError('That is not a valid restriction code')
        self.set_field('restrictionCode', restrictionCode)

    def get_restrictionCode(self):
        return self.get_field('restrictionCode')

    def set_restrictionReason(self, restrictionReason):
        """
        set the instances restriction reason

        __Args__

        1. restrictionReason (str): an explanation of why the file is
        restricted
        """
        self.set_field('restrictionReason', restrictionReason)

    def add_restrictionReason(self, restrictionReason):
        """
        Add to the files existing restrictionReasons

        __Args__

        1. restrictionReason (str): an explanation of why the file is
        restricted
        """
        self.add_to_field('restrictionReason', restrictionReason)

    def get_restrictionReason(self):
        return self.get_field('restrictionReason')

    def set_donorStipulation(self, donorStipulation):
        """
        set the files donor stipulation

        __Args__

        1. donorStipulation (str): a restriction stipulation the donor
        enforces on the file
        """
        self.set_field('donorStipulation', donorStipulation)

    def add_donorStipulation(self, donorStipulation):
        """
        Add to the files existing donor stipulations

        __Args__

        1. donorStipulation (str): a restriction stipulation the donor
        enforces on the file
        """
        self.add_to_field('donorStipulation', donorStipulation)

    def get_donorStipulation(self):
        return self.get_field('donorStipulation')

    def set_linkingObjectIdentifier(self, linkingObjectIdentifier):
        self.set_field('linkingObjectIdentifier', linkingObjectIdentifier)

    def add_linkingObjectIdentifier(self, linkingObjectIdentifier):
        self.add_to_field('linkingObjectIdentifier', linkingObjectIdentifier)

    def get_linkingObjectIdentifier(self):
        return self.get_field('linkingObjectIdentifier')

    def set_linkingAgentIdentifier(self, linkingAgentIdentifier):
        """
        set the LinkingAgentIdentifier associated with this restriction

        __Args__

        1. linkingAgentIdentifier(PremisNode.LinkingAgentIdentifier):
            the linking agent identifier node of the agent associated
            with the restriction.
        """
        self.set_field('linkingAgentIdentifier', linkingAgentIdentifier)

    def add_linkingAgentIdentifier(self, linkingAgentIdentifier):
        """
        Add to the file's restriction's existing linkingAgentIdentifiers

        1. linkingAgentIdentifier(PremisNode.LinkingAgentIdentifier):
            the linking agent identifier node of the agent associated
            with the restriction.
        """
        self.add_to_field('linkingAgentIdentifier', linkingAgentIdentifier)

    def get_linkingAgentIdentifier(self):
        return self.get_field('linkingAgentIdentifier')

    def set_linkingRightsExtensionIdentifier(self, linkingRightsExtensionIdentifier):
        self.set_field('linkingRightsExtensionIdentifier', linkingRightsExtensionIdentifier)

    def add_linkingRightsExtensionIdentifier(self, linkingRightsExtensionIdentifier):
        self.add_to_field('linkingRightsExtensionIdentifier', linkingRightsExtensionIdentifier)

    def get_linkingRightsExtensionIdentifier(self):
        return self.get_field('linkingRightsExtensionIdentifier')

    def set_active(self, active):
        """
        set the instances active attribute

        __Args__

        1. active (str||bool): "True" or "False" to denote whether
        the restriction is active
        """
        self.set_field('active', str(active))

    def get_active(self):
        return self.get_field('active')
