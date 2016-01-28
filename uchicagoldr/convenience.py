from uchicagoldrconfig.LDRConfiguration import LDRConfiguration

def get_valid_types():
   config = LDRConfiguration()
   types = config.get_a_config_data_value('outputinformation', 'valid_types')
   a_list = types.split(',')
   return a_list
