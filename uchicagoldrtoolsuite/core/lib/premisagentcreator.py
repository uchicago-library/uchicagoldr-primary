from pypremis.nodes import Agent, AgentIdentifier, AgentExtension


class PremisAgentCreator(object):

    @classmethod
    def make_agent(cls,
                   agentIdentifierType,
                   agentIdentifierValue,
                   agentName,
                   agentType,
                   department=None,
                   cnet=None,
                   agentRole=None
                   ):
        agent = cls._build_agent(agentIdentifierType, agentIdentifierValue,
                                 agentName, agentType, department, cnet,
                                 agentRole)
        return agent

    @classmethod
    def _build_agent(cls, agentIdentifierType, agentIdentifierValue,
                     agentName, agentType, department, cnet, agentRole):
        agentIdentifier = cls._build_agentIdentifier(
            agentIdentifierType,
            agentIdentifierValue
        )

        agent = Agent(agentIdentifier)

        agent.set_agentName(agentName)

        agent.set_agentType(agentType)

        agent.set_agentName(agentName)

        if department is not None or \
                cnet is not None or \
                agentRole is not None:
            agent.set_agentExtension(
                cls._build_agentExtension(
                    department, cnet, agentRole
                )
            )

        return agent

    @classmethod
    def _build_agentIdentifier(cls, agentIdentifierType, agentIdentifierValue):
        return AgentIdentifier(agentIdentifierType, agentIdentifierValue)

    @classmethod
    def _build_agentExtension(cls, department, cnet, agentRole):
            agentExtension = AgentExtension()
            if department is not None:
                agentExtension.set_field('department', department)
            if cnet is not None:
                agentExtension.set_field('cnet', cnet)
            if agentRole is not None:
                agentExtension.set_field('agentRole', agentRole)
            return agentExtension
