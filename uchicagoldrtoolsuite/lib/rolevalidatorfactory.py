"""
The RoleValidatorFactory shold be used to instantiate a validator for a given role's input
"""
from typing import NamedTuple
from stagervalidator import StagerValidator

class RoleValidatorFactory(object):
    """The RoleValidatorFactory builds validators for every role's input
    """
    def __init__(self, factory_type: str):
        self.order = factory_type

    def build(self, data: NamedTuple("info",[('data',dict)])):
        """A series of conditionals to determine (based on the initialized order 
        data member on the class) what type of validator instance to return.
        """
        if self.order == 'staging':
            if not data:
                raise ValueError("to create an instance of this class extra information is required")
            return StagerValidator(data)
        else:
            raise ValueError("{} is not a valid role validator".format(self.order))
