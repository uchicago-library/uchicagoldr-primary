from logging import getLogger

from pypremis.nodes import Agent


log = getLogger(__name__)


class AgentProxy(object):
    def __init__(self, identifier=None, name=None,
                 retriever=None, updater=None, minter=None):
        self._record = None
        self._retriever = None
        self._updater = None
        self._minter = None
        self._identifier = None
        self._identifierType = None

        if identifier is None and name is None:
            raise ValueError(
                "Must provide a name and/or an identifier. Note the " +
                "identifier will always take precedence when provided."
            )

        self.retriever = retriever
        self.updater = updater
        self.minter = minter
        self.identifier = identifier
        self.name = name

    def sync(self):
        self.updater(self.record)

    def get_record(self):
        if self._record is None:
            try:
                if self.identifier:
                    self.record = self._retrieve_record(self.identifier)
                else:
                    self.record = self._search_for_record(self.name)[0]
            except Exception as e:
                if self.minter is None:
                    raise e
                else:
                    log.info(
                        "No agent existed, minting a new Agent"
                    )
                    self.record = self.minter(self.name)
        return self._record

    def set_record(self, x):
        if not isinstance(x, Agent):
            raise TypeError()
        self._record = x

    def get_retriever(self):
        return self._retriever

    def set_retriever(self, x):
        self._retriever = x

    def get_updater(self):
        return self._updater

    def set_updater(self, x):
        self._updater = x

    def get_minter(self):
        return self._minter

    def set_minter(self, x):
        self._minter = x

    def _retrieve_record(self, ident):
        return self.retriever.retrieve(ident)

    def _search_for_record(self, name):
        return self.retriever.search(name)

    record = property(get_record, set_record)
    retriever = property(get_retriever, set_retriever)
    updater = property(get_updater, set_updater)
    minter = property(get_minter, set_minter)
