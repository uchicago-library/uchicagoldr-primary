from abc import ABCMeta

from .abc.retriever import Retriever
from ..family import Family

__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class FamilyRetriever(Retriever, metaclass=ABCMeta):
    def pack(self, family_type, identifier, name, child_families,
             child_content_pointers, record_identifier):
        return Family(family_type, identifier=identifier, name=name,
                      child_families=child_families,
                      child_content_pointers=child_content_pointers,
                      record_identifier=record_identifier)


    def retrieve_children(self, family):
        for x in family.get_children():
            yield self.retrieve(x)
