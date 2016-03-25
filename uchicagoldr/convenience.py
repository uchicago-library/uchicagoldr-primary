
from uchicagoldr.ldrconfiguration import LDRConfiguration

def get_valid_types():
   config = LDRConfiguration()
   types = config.get_a_config_data_value('outputinformation', 'valid_types')
   a_list = types.split(',')
   return a_list

def sane_hash(hash_algo, file_path, block_size=65536):
    from hashlib import md5, sha256
    if hash_algo == 'md5':
        hasher = md5
    elif hash_algo == 'sha256':
        hasher = sha256
    else:
        raise NotImplemented('Hashing algos supported are md5 and sha256')

    hash_result = hasher()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(block_size)
            if not data:
                break
            hash_result.update(data)
    return str(hash_result.hexdigest())
