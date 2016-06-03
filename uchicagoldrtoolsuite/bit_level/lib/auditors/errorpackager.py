
__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class ErrorPackager(object):
    """The ErrorPackager class is meant as a delegate to an auditor class
    """

    class Error(object):
        """The Error class is held in a list in the ErrorPackager data attributes.
        It gets called when an auditor calls errorpackger.add() with the
        category and the error messsage.
        """
        def __init__(self, category, message):
            """instantiates an Error class

            __ArgS__
            1. category (str): the type of error that this represents
            2. message (str): the string describing what went wrong
            """
            self.category = category
            self.message = message

        def __str__(self):
            """returns a string representation of the error
            """
            return "category: {}\nmessage: {}".format(self.category,
                                                      self.message)

    def __init__(self):
        """initializes an errorpackager with an empty errors attribute list
        and a numErrors attribute of 0
        """
        self.errors = []
        self.numErrors = 0

    def get_errors(self):
        """returns the data attribute errors
        """
        return self._errors

    def set_errors(self, value):
        """sets the errors data attribute value
        """
        self._errors = value

    def add(self, category, message):
        """creates a new Error and adds it to the errors data attribute value list

        __Args__
        1. category (str): the kind of error that this is
        2. message (str): an informative string representing what exactly
        was wrong that resulted in this error
        """
        new_error = self.Error(category, message)
        self.numErrors += 1
        self.errors.append(new_error)

    def display(self):
        """returns a list of errors as strings
        """
        output = []
        for n_error in self.errors:
            output.append(str(n_error))
        return output

    errors = property(get_errors, set_errors)
