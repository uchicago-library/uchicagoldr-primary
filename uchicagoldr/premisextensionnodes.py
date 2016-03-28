from pypremis.nodes import ExtensionNode
from controlledvocab.lib import ControlledVocabulary as CV


class Restriction(ExtensionNode):

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

    def __init__(self, restrictionCode, active):
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

    def set_restrictionCode(self, restrictionCode):
        """
        set the instances restriction code

        __Args__

        1. restrictionCode(str): a restriction code
        """
        if restrictionCode not in self.restriction_code_cv:
            raise ValueError('That is not a valid restriction code')
        self.set_field('restrictionCode', restrictionCode)

    def set_active(self, active):
        """
        set the instances active attribute

        __Args__

        1. active (str||bool): "True" or "False" to denote whether
        the restriction is active
        """
        self.set_field('active', str(active))

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
