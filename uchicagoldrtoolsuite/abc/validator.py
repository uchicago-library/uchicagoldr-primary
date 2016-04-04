"""An abstract class for validators
"""
class Validator:
    """The Validator class should be used as the base class for all role validators
    """
    def test(self, info: dict) -> bool:
        """A method for testing whether a given input passes the test for a role validator
        """
        raise NotImplementedError()


    def verbose_test(self, info: dict) -> str:
        """A method for testing whether a given input passes the validation test
        and to return a string explaining what went wrong
        """
        raise NotImplementedError()


    def get_info_needed(self) -> dict:
        """A method for returning the information that needs to be derived from the input
        in order to complete validation.
        """
        raise NotImplementedError()


    def is_required_info_present(self) -> bool:
        """A method for checking if the information required in order to complete
        validation has been calculated.
        """
        raise NotImplementedError()
