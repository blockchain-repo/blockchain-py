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
import crypto
import os
from hostlist import public_dns_names, public_hosts

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

old_keypairs_list = [] # 旧的keypairs list 信息
need_gen_count = num_pairs

# 判断是否存在keypais file,不存在则
if exist_keypairs_file:
    # 获取旧的keypairs信息
    try:
         from keypairs import keypairs_list
         len_keypairs = len(keypairs_list)
         if len_keypairs == 0:
             old_keys = []
         elif len_keypairs > num_pairs:
             exit("The keypairs exist can no")
         else:
             need_gen_count = num_pairs - len_keypairs
             for keypairs in keypairs_list:
                 old_keypairs_list.append(keypairs)
    except Exception as ex:
        print('keypairs error ,need rewrite!')
else:
    old_keypairs_list = []

# 生成长度为 num_pairs 的keypairs, 并append到new_sort_key_pairs
def generate_keypairs(need_gen_count):
    for i in range(need_gen_count):
        keypair = crypto.generate_key_pair()
        item = (keypair[0], keypair[1])
        old_keypairs_list.append(item)
        print("new generate keypairs with key={}".format(keypair[1]))


def write_keypairs(old_keypairs_list):
    generate_keypairs(need_gen_count=need_gen_count)
    with open('keypairs.py', 'w') as f:
        f.write('# -*- coding: utf-8 -*-\n')
        f.write('"""A set of keypairs for use in deploying\n')
        f.write('UnichainDB servers with a predictable set of keys.\n')
        f.write('"""\n')
        f.write('\n')
        f.write('from __future__ import unicode_literals\n')
        f.write('\n')
        f.write('keypairs_list = [')
        for pair_num in range(num_pairs):
            spacer = '' if pair_num == 0 else '    '
            f.write("{}('{}',\n     '{}'),\n".format(
                spacer, old_keypairs_list[pair_num][0], old_keypairs_list[pair_num][1]))
        f.write('    ]\n')

write_keypairs(old_keypairs_list)
print("Total {} nodes info in keypairs file!".format(num_pairs))
print('Done.')
