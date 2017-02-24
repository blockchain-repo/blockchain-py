from bigchaindb.common.crypto import generate_key_pair

class GenPublickeyTest(object):

    def get_key_pair(self):
        return generate_key_pair()


if __name__ == "__main__":
    testcase = GenPublickeyTest()
    public_key,private_key = testcase.get_key_pair()
    print ("Gen public&private key:")
    print ("    public key     : " + str(public_key))
    print ("    public key len : %d" % len(public_key))
    print ("    private key    : " + str(private_key))
    print ("    public key len : %d" % len(public_key))
