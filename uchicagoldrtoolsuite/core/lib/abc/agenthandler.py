from abc import ABCMeta, abstractmethod

class AgentHandler(metaclass=ABCMeta):

    _target_agentName = None
    _target_agentIdentifier = None
    _agent_record = None

    def __init__(self, agentIdentifier=None, agentName=None):
        if agentIdentifier is None and \
                agentName is None:
            raise ValueError("You must provide exactly one of the kwargs " +
                             "in order to retrieve an agent record.")
        if agentIdentifier is not None and \
                agentName is not None:
            raise ValueError("You must provide exactly one of the kwargs " +
                             "in order to retrieve an agent record.")
        if agentIdentifier is not None:
            self.target_agentIdentifier = agentIdentifier
        if agentName is not None:
            self.target_agentName = agentName
        self.target_agent = agentName

    def retrieve_agent_record(self):
        if self.get_target_agentIdentifier() is not None:
            self.set_agent_record(
                self.retrieve_agent_by_identifier()
            )
        else:
            self.set_agent_record(
                self.search_for_agent_by_name()
            )
        return self.get_agent_record()

    def get_agentIdentifiers_from_record(self, premis):
        ids = []
        for a in premis.get_agent_list():
            ids.append(
                (
                    a.get_agentIdentifier()[0].get_agentIdentifierType(),
                    a.get_agentIdentifier()[0].get_agentIdentifierValue()
                 )
            )
        return ids

    def get_agentNames_from_record(self, premis):
        names = []
        for a in premis.get_agent_list():
            names.append(
                a.get_agentName()
            )
        return names

    @abstractmethod
    def retrieve_agent_by_identifier(self):
        raise NotImplementedError()

    @abstractmethod
    def search_for_agent_by_name(self):
        raise NotImplementedError()

    @abstractmethod
    def write_agent_record(self):
        raise NotImplementedError()

    def get_target_agentName(self):
        return self._target_agentName

    def set_target_agentName(self, x):
        self._target_agentName = x

    def get_target_agentIdentifier(self):
        return self._target_agentIdentifier

    def set_target_agentIdentifier(self, x):
        self._target_agentIdentifier = x

    def get_agent_record(self):
        return self._agent_record

    def set_agent_record(self, x):
        self._agent_record = x

    target_agentName = property(get_target_agentName, set_target_agentName)
    target_agentIdentifier = property(get_target_agentIdentifier, set_target_agentIdentifier)
    agent_record = property(get_agent_record, set_agent_record)
