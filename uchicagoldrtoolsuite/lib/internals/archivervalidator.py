"""
The ArchiverValidator is used to determine whether the input given to a particular
instance of the Stager class is valid or not.
"""

from abc.validator import Validator

class ArchiverValidator(Validator):
    """The StagerValidator is a class that will test whether the given tree view
    of a potential stageable directory can be staged.
    """
    def __init__(self, necessary_info):
        self.data = necessary_info

    def is_required_info_present(self) -> bool:
        """A method to check if the validator has all the information it needs
        to make its decision
        """
        if not getattr(self.data,
                       'numfiles', None) and\
        not getattr(self.data,
                    'numfilesfound', None):
            return False
        return True


    def test(self, processor_info: dict) -> bool:
        """A function to test whether the given input is a valid directory to be staged.
        """
        self.is_required_info_present()
        numfilesfound = processor_info.get('numfilesfound')
        numfiles = processor_info.get('numfiles')
        numfolders = processor_info.get('numfolders')
        numfoldersfound = processor_info.get('numfoldersfound')
        accessionrecordpresent = processor_info.get('accessionrecordpresent')
        premisobjectsfound = processor_info.get('processorobjectsfound')
        legalnotepresent = processor_info.get('legalnotepresent')
        adminnotepresent = processor_info.get('adminnotepresent')
        numtechmdata = processor_info.get('numtechmdata')
        return numfilesfound == numfiles and numfoldersfound == numfolders \
            and premisobjectsfound == numtechmdata and accessionrecordpresent \
            and legalnotepresent and adminnotepresent
									
    def get_info_needed(self):
    	return {'numfilesfound':int, 'numfoldersfound':int,'numtechmdata':int,
                'acessionrecordpresent':bool, 'premisobjectsfound':int,
                'legalnotepresent':bool, 'adminnotepresent':bool}


    def verbose_test(self, processor_info: dict) -> str:
        """A function to test whether the given input is a valid directory and return
        an explanation of success/fail
        """
        self.is_required_info_present(self)
        number_of_files_found = processor_info.get('numfilesfound')
        numfilesfound = processor_info.get('numfilesfound')
        numfiles = processor_info.get('numfiles')
        numfolders = processor_info.get('numfolders')
        numfoldersfound = processor_info.get('numfoldersfound')
        accessionrecordpresent = processor_info.get('accessionrecordpresent')
        premisobjectsfound = processor_info.get('processorobjectsfound')
        legalnotepresent = processor_info.get('legalnotepresent')
        adminnotepresent = processor_info.get('adminnotepresent')
        numtechmdata = processor_info.get('numtechmdata')
        
        if numfiles != number_of_files_found:
            return ("fatal", "There were {} files actually found,".format(number_of_files_found) +\
                "but you said there should be {} files".format(self.data.validation.get('numfiles')))
        elif premisobjectsfound != numtechmdata:
            return ("fatal", "There are {} premis objects found".format(premisobjectsfound) +\
                    "and there are {} technical mdata files found".format(numtechmdata))
                                                                        
        elif numfolders != numfoldersfound:
            return ("fatal", "There are {} runs found".format(numfoldersfound) +\
                    "but you said there would be {} runs".format(numfolders))
        elif not accessrecordpresent:
            return ("fatal", "There is no accession record present")
        elif not legalnotepresent:
            return ("fatal", "There is no legal note present")
        elif not adminnotepresent:
            return ("fatal", "There is no admin note present")        
