"""An abstract class for validators
"""
class Validator(object):
    """The Validator class should be used as the base class for all role validators
    """
    def __init__(self, order):
        self.order = order
        self.result = None
        self.explanation = "not applicable"

    def test(self):
        """A method for testing whether a given input passes the test for a role validator
        """
        self.result = False

    def verbose_test(self) -> str:
        """A method for testing whether a given input passes the validation test
        and to return a string explaining what went wrong
        """
        self.explanation = "not implemented"


    def get_result(self):
        """method to get the value of the result data member
        """
        return self.result

    def set_result(self, value):
        """method to set a value of the data member result
        """
        if not isinstance(value, bool):
            raise ValueError("result can only be True or False")
        self.result = value

    def get_explanation(self):
        """method to get the value of the data member explanation
        """
        return self.explanation

    def set_explanation(self, value):
        """method to set the value of the data member explanation
        """
        if not isinstance(value, str):
            raise ValueError("expalantion must be a string")
        self.explanation = value

    result = property(get_result, set_result)
    explanation = property(get_explanation, set_explanation)

