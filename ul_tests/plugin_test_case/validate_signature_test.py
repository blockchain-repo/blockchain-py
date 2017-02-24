from bigchaindb.common.util import serialize
from bigchaindb.common.crypto import generate_key_pair,SigningKey,VerifyingKey

class ValidateSignatureTest(object):

    def __init__(self):
        pass  

    def sign(self, signing_dict, signing_key):
        signing_str = serialize(signing_dict)
        signing_key = SigningKey(signing_key)
        return signing_key.sign(signing_str.encode()).decode()


if __name__ == "__main__":
    test_case = ValidateSignatureTest()
    #gen key paire
    private_key,public_key = generate_key_pair()
    #print (SigningKey(private_key).get_verifying_key().encode().decode())
    print ("\nnode pubkey&prikey is:")
    print ("    public  key is:" + str(public_key))
    print ("    private key is:" + str(private_key))
    #sign transation
    payload = {"payload":"test signature"}
    print ("\npayload is:" + str(payload)) 
    signature = test_case.sign(payload, private_key)
    print ("\nthe signature of payload is:" + str(signature))

    #check signature pass
    print ("\n====when payload is valid====")
    check_public_key = VerifyingKey(public_key)
    check_res = check_public_key.verify(serialize(payload).encode() ,signature)
    print ("check signature result:" + str(check_res))
    #check signature not pass
    payload_new = {"payload":"test signature invalid"}
    print ("\n====when payload is novalid====")
    print ("old payload is:" + str(payload))
    print ("new payload is:" + str(payload_new))
    check_public_key = VerifyingKey(public_key)
    check_res = check_public_key.verify(serialize(payload_new).encode() ,signature)
    print ("check signature result:" + str(check_res))
