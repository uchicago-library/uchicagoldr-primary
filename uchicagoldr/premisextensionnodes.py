from pypremis.nodes import ExtensionNode

class Restriction(ExtensionNode):
    def __init__(self, restrictionCode, active):
        ExtensionNode.__init__(self)
        self.set_restrictionCode(restrictionCode)
        self.set_active(active)

    def set_restrictionCode(self, restrictionCode):
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
