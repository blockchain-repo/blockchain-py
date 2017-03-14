import time
import datetime
import sha3
import rapidjson
from cryptoconditions import crypto

class ValidateSignatureTest(object):

    def __init__(self):
        pass

    def sign(self, signing_dict, signing_key):
        signing_str = self.serialize(signing_dict)
        signing_key = crypto.Ed25519SigningKey(signing_key)
        return signing_key.sign(signing_str.encode()).decode()


    def hash_data(data):
        return sha3.sha3_256(data.encode()).hexdigest()


    def generate_key_pair(self):
        private_key, public_key = crypto.ed25519_generate_key_pair()
        return private_key.decode(), public_key.decode()

    def gen_timestamp(self):
        return str(round(time.time() * 1000))

    def serialize(self, data):
        return rapidjson.dumps(data, skipkeys=False, ensure_ascii=False,
                               sort_keys=True)

    def deserialize(self, data):
        return rapidjson.loads(data)


if __name__ == "__main__":
    test_case = ValidateSignatureTest()
    private_key,public_key = test_case.generate_key_pair()
    lun_begin_time = test_case.gen_timestamp()
    while ((int(test_case.gen_timestamp()) - int(lun_begin_time))<=1000):
        begin_time = test_case.gen_timestamp()
        #sign transation
        payload = {"payload":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}
        signature = test_case.sign(payload, private_key)
        #check signature node1
        check_public_key1 = crypto.Ed25519VerifyingKey(public_key)
        check_res1 = check_public_key1.verify(test_case.serialize(payload).encode() ,signature)
        end_time = test_case.gen_timestamp()
        now_date = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print ("[%s]test case: %s" % (now_date, str(int(end_time) - int(begin_time))))
