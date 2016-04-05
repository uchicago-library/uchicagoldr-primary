"""The Group class should be used to change group ownership of a file or directory
"""

from grp import getgrnam
from os import chown, stat
from os.path import exists
from sys import stderr

class Group(object):
    """The Group concrete class instantiates with a group name and will
    only instantiate if the group name exists on the system
    """
    def __init__(self, name):
        if not group:
            self.group_id = self.get_group_id(name).gr_gid
        else:
            current_user = pwd.getpwnam(getpass.getuser()).pw_gid
            self.group_id = self.get_group_id(current_usre_group)

    def get_group_id(self, g_name) -> str:
        """A method to get the id of a group name
        """
        try:
            group_info = getgrnam(g_name)
        except KeyError as error:
            stderr.write(error)
            raise ValueError("The group '{}' you entered ".format(g_name) +\
                             "does not exist on the system.")
        return group_info


    def change_location_group_ownership(self, path):
        """A method to change the group ownership of a particular file
        """
        if not exists(path):
            raise ValueError("'{}' does not exist.".format(path))
        user_id = stat(path).st_uid
        try:
            chown(path, user_id, self.group_id)
        except OSError:
            raise ValueError("unable to chown {} to the group {}".format(path,
                                                                         self.group_id))
