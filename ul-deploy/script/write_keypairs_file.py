"""A Python 3 script to write a file with a specified number
of keypairs, using bigchaindb.crypto.generate_key_pair()
The written file is always named keypairs.py and it should be
interpreted as a Python 2 script.

Usage:
    $ python3 write_keypairs_file.py num_pairs

Using the list in other Python scripts:
    # in a Python 2 script:
    from keypairs import keypairs_list
    # keypairs_list is a list of (sk, pk) tuples
    # sk = signing key (private key)
    # pk = verifying key (public key)
"""

import argparse
from bigchaindb.common import crypto
from hostlist import public_dns_names,public_hosts
import os

# Parse the command-line arguments
desc = 'Write a set of keypairs to keypairs.py'
parser = argparse.ArgumentParser(description=desc)
parser.add_argument('num_pairs',
                    help='number of keypairs to write',
                    type=int)
args = parser.parse_args()
num_pairs = int(args.num_pairs)

# Generate and write the keypairs to keypairs.py
print('Writing {} keypairs to keypairs.py...'.format(num_pairs))

exist_keypairs_file = os.path.isfile('keypairs.py')

new_sort_keys = public_hosts # 节点信息,有序 根据这个顺序生成新的keypairs list
old_sort_keys = [] # 旧的keypairs list对应的key信息
new_sort_key_pairs = [] # 按照节点信息生成的新的,包含旧的无用节点keypairs信息的完整keypairs list

# 判断是否存在keypais file,不存在则
if exist_keypairs_file:
    # 获取旧的keypairs信息
    try:
         from keypairs import keypairs_list
         if len(keypairs_list) == 0:
             old_sort_keys = []
         else:
             for keypairs in keypairs_list:
                 for key, value in keypairs.items():
                     old_sort_keys.append(key)
                # print(old_sort_keys)
    except Exception as ex:
        print('keypairs_list error ,need rewrite!')
else:
    old_sort_keys = []

# 根据传入的keypairs_keys (list) 生成keypairs,并append到new_sort_key_pairs
def append_keypairs(keypairs_keys):
    isList = isinstance(keypairs_keys,list)

    if not isList:
        raise Exception("keypairs_keys must be the type of list")

    for keypairs_key in keypairs_keys:
        keypair = crypto.generate_key_pair()
        item = {keypairs_key: (keypair[0], keypair[1])}
        new_sort_key_pairs.append(item)

def generate_keypirs(old_sort_keys,new_sort_keys):
    # 如果不存在旧的keypairs 信息就新生成所有信息
    if len(old_sort_keys) == 0:
        # 按顺序生成keypairs
        append_keypairs(new_sort_keys)
    else:
        # 如果存在旧的keypairs,则按照节点信息顺序依次判断是否存在旧的keypairs,存在取出,不存在生成
        for new_pairs_key in new_sort_keys:
            if new_pairs_key in old_sort_keys:
                new_in_old_index = old_sort_keys.index(new_pairs_key)
                print("new_pairs_key:\t{}\texists in old_sord_keys index: {}".format(new_pairs_key,new_in_old_index))
                new_sort_key_pairs.append(keypairs_list[new_in_old_index])

            else:
                append_keypairs([new_pairs_key])
                # print('new nodes key:\t{}\tnot exists and add it, now is:\n{}'.format(new_pairs_key,new_sort_key_pairs))

        # 处理nodes信息中不存在,但是存在与keypairs列表中的信息
        print("old_sort_keys {}".format(old_sort_keys))
        print("new_sort_keys {}".format(new_sort_keys))
        minus_keypairs_list_keys = list(set(old_sort_keys).difference(new_sort_keys))
        print("minus_keypairs_list_keys {}".format(minus_keypairs_list_keys))
        for minus_keypairs_list_key in minus_keypairs_list_keys:
            minus_old_index = old_sort_keys.index(minus_keypairs_list_key)
            print("minus_old_index:\t{}\texists in old_sord_keys index: {}".format(minus_keypairs_list_key, minus_old_index))
            new_sort_key_pairs.append(keypairs_list[minus_old_index])

def write_keypairs(keypairs_list):
    with open('keypairs.py', 'w') as f:
        f.write('# -*- coding: utf-8 -*-\n')
        f.write('"""A set of keypairs for use in deploying\n')
        f.write('BigchainDB servers with a predictable set of keys.\n')
        f.write('"""\n')
        f.write('\n')
        f.write('from __future__ import unicode_literals\n')
        f.write('\n')
        f.write('keypairs_list = [')
        index = 0
        for keypairs in keypairs_list:
            for key_pair_key, keypair in keypairs.items():
                spacer = '' if index == 0 else '    '
                f.write("{}{{'{}':('{}',\n     '{}')}},\n".format(
                    spacer, key_pair_key, keypair[0], keypair[1]))
            index += 1
        f.write('    ]\n')

generate_keypirs(old_sort_keys,new_sort_keys)
write_keypairs(new_sort_key_pairs)
print("You have configure {} nodes, total {} nodes info in keypairs!".format(len(new_sort_keys),len(new_sort_key_pairs)))
print('Done.')
