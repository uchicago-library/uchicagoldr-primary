from uchicagoldr.ldrconfiguration import LDRConfiguration


def get_valid_types():
    config = LDRConfiguration()
    types = config.get_a_config_data_value('outputinformation', 'valid_types')
    a_list = types.split(',')
    return a_list


def sane_hash(hash_algo, file_path, block_size=65536):
    """
    compute a hash hexdigest without loading giant things into RAM

    __Args__

    1. hash_algo (str): an algo with an implementation hooked
        - md5
        - sha256
    2. file_path (str): the abspath to the file

    __KWArgs__

    * block_size (int): How many bytes to load into RAM at once

    __Returns__

    * (str): The hexdigest of the specified hashing algo on the file
    """
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
           try:
              data = f.read(block_size)
           except OSError as e:
              stderr.write("{} could not be read\n".format(file_path))
              stderr.write(e)
              Stderr.write("\n")
           if not data:
              break
           hash_result.update(data)
    return str(hash_result.hexdigest())
