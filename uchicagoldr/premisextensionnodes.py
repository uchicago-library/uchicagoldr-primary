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
        ExtensionNode.__init__(self)
        self.set_restrictionCode(restrictionCode)
        self.set_active(active)

    def set_restrictionCode(self, restrictionCode):
        if restrictionCode not in self.restriction_code_cv:
            raise ValueError('That is not a valid restriction code')
        self.set_field('restrictionCode', restrictionCode)

    def set_active(self, active):
        self.set_field('active', str(active))

    def set_restrictionReason(self, restrictionReason):
        self.set_field('restrictionReason', restrictionReason)

    def add_restrictionReason(self, restrictionReason):
        self.add_to_field('restrictionReason', restrictionReason)

    def set_donorStipulation(self, donorStipulation):
        self.set_field('donorStipulation', donorStipulation)

    def add_donorStipulation(self, donorStipulation):
        self.add_to_field('donorStipulation', donorStipulation)

    def set_linkingAgentIdentifier(self, linkingAgentIdentifier):
        self.set_field('linkingAgentIdentifier', linkingAgentIdentifier)

    def add_linkingAgentIdentifier(self, linkingAgentIdentifier):
        self.add_to_field('linkingAgentIdentifier', linkingAgentIdentifier)
