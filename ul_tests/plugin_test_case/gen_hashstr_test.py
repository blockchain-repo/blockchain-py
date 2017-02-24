from bigchaindb.common.util import serialize
from bigchaindb.common.crypto import hash_data

class GenHashstrTest(object):

    def get_serialize_data(self, p_dict):
        return serialize(p_dict)

    def get_hash_str(self, p_str):
        return hash_data(p_str)


if __name__ == "__main__":
    testcase = GenHashstrTest()
    t_dict_1 = {"payload": "test make payload 1"}
    t_dict_2 = {"payload": "test make payload 2"}
    t_json_1 = testcase.get_serialize_data(t_dict_1)
    t_json_2 = testcase.get_serialize_data(t_dict_2)
    print ("Gen Hash str:")
    print ("    test dict 1:" + str(t_dict_1))
    print ("    test str  1:" + t_json_1)
    print ("    test hash 1:" + testcase.get_hash_str(t_json_1))
    print ("    len  hash 1: %d" % len(testcase.get_hash_str(t_json_1)))
    print ("")
    print ("    test dict 2:" + str(t_dict_2))
    print ("    test str  2:" + t_json_2)
    print ("    test hash 2:" + testcase.get_hash_str(t_json_2))
    print ("    len  hash 2: %d" % len(testcase.get_hash_str(t_json_2)))
