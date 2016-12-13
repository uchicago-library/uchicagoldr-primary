from logging import getLogger

from pypremis.nodes import Agent

from uchicagoldrtoolsuite import log_aware
from .convenience import class_or_callable, log_init_attempt, log_init_success


log = getLogger(__name__)


class AgentProxy(object):
    @log_aware(log)
    def __init__(self, identifier=None, name=None,
                 retriever=None, searcher=None, updater=None, minter=None):
        log_init_attempt(self, log, locals())
        self._record = None
        self._retriever = None
        self._searcher = None
        self._updater = None
        self._minter = None
        self._identifier = None
        self._name = None

        self._identifier = identifier
        self._name = name
        self.retriever = retriever
        self.searcher = searcher
        self.updater = updater
        self.minter = minter
        log_init_success(self, log)

    @log_aware(log)
    def sync(self):
        return class_or_callable(self.updater, 'update', self.record)

    @log_aware(log)
    def get_record(self):
        if self._record is None:
            try:
                if self._identifier:
                    self.record = self._retrieve_record(self._identifier)
                else:
                    records = self._search_for_record(self._name)
                    if len(records) > 1:
                        raise ValueError("Multiple Agents matched that query!")
                    if len(records) < 1:
                        raise ValueError("No Agents matched that query!")
                    self.record = records[0]
            except Exception as e:
                if self.minter is None:
                    raise e
                else:
                    log.info(
                        "No agent existed, minting a new Agent"
                    )
                    self.record = self.minter(self._identifier, self._name)
        return self._record

    @log_aware(log)
    def set_record(self, x):
        if not isinstance(x, Agent):
            raise TypeError()
        self._record = x

    @log_aware(log)
    def get_retriever(self):
        return self._retriever

    @log_aware(log)
    def set_retriever(self, x):
        self._retriever = x

    @log_aware(log)
    def get_searcher(self):
        return self._searcher

    @log_aware(log)
    def set_searcher(self, x):
        self._searcher = x

    @log_aware(log)
    def get_updater(self):
        return self._updater

    @log_aware(log)
    def set_updater(self, x):
        self._updater = x

    @log_aware(log)
    def get_minter(self):
        return self._minter

    @log_aware(log)
    def set_minter(self, x):
        self._minter = x

    @log_aware(log)
    def _retrieve_record(self, ident):
        return class_or_callable(self.retriever, 'retrieve', ident)

    @log_aware(log)
    def _search_for_record(self, name):
        return class_or_callable(self.searcher, 'search', name)

    record = property(get_record, set_record)
    retriever = property(get_retriever, set_retriever)
    searcher = property(get_searcher, set_searcher)
    updater = property(get_updater, set_updater)
    minter = property(get_minter, set_minter)


from functools import partial

from .agentlib import api_retrieve_agent, api_search_agent, api_update_agent, \
    mint_agent


class APIAgentProxy(AgentProxy):
    def __init__(self, api_root, identifier=None, name=None):
        # Note at the moment this lacks a minter, until some of the trickier
        # bits of the agents interface can be worked out.
        super().__init__(
            identifier, name,
            retriever=partial(api_retrieve_agent, api_root),
            searcher=partial(api_search_agent, api_root),
            updater=partial(api_update_agent, api_root)
        )
