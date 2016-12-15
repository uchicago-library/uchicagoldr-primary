from abc import ABCMeta, abstractmethod

class IAgent(metaclass=ABCMeta):
   @abstractmethod
   def get_premis_agent_record(self):
       pass

   @abstractmethod
   def write_premis_agent_record(self):
       pass
