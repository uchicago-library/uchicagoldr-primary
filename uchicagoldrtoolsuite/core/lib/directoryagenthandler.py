from .abc.agenthandler import AgentHandler
from os import scandir
from os.path import join

from pypremis.lib import PremisRecord


class DirectoryAgentHandler(AgentHandler):

    _agents_dir = None

    def __init__(self, agents_dir, agentIdentifier=None, agentName=None):
        self.agents_dir = agents_dir
        super().__init__(agentIdentifier, agentName)

    def retrieve_agent_by_identifier(self):
        print(self.agents_dir)
        for x in scandir(self.agents_dir):
            x = x.name
            look_for = self.target_agentIdentifier + ".premis.xml"
            print(x)
            print(look_for)
            if x == look_for:
                pr = PremisRecord(frompath=join(self.agents_dir, look_for))
                assert(len(pr.get_agent_list()) == 1)
                assert(self.get_agentIdentifiers_from_record(pr)[0][1] == self.target_agentIdentifier)
                a = pr.get_agent_list()[0]
                return a
        raise ValueError("That identifier doesn't appear to exist " +
                         "in {}".format(self.agents_dir))

    def search_for_agent_by_name(self):
        for x in scandir(self.agents_dir):
            x = x.name
            file_name = join(self.agents_dir, x)
            pr = PremisRecord(frompath=file_name)
            for a in pr.get_agent_list():
                names = a.get_agentName()
                for n in names:
                    if n == self.target_agentName:
                        return a
        raise ValueError("That agentName ({}) ".format(self.target_agentName) +
                         "doesn't appear to exist " +
                         "in {}".format(self.agents_dir))

    def write_agent_record(self):
        id_str = self.agent_record.get_agentIdentifier()[0].get_agentIdentifierValue()
        target_file = join(self.agents_dir, id_str+".premis.xml")
        pr = PremisRecord(agents=[self.agent_record])
        pr.write_to_file(target_file)

    def get_agents_dir(self):
        return self._agents_dir

    def set_agents_dir(self, x):
        self._agents_dir = x

    agents_dir = property(get_agents_dir, set_agents_dir)
