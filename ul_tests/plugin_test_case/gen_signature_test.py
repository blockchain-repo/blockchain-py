from bigchaindb.common.util import serialize
from bigchaindb.common.crypto import generate_key_pair,SigningKey,VerifyingKey
from bigchaindb.models import Transaction,Asset
from bigchaindb import Bigchain

class GenSignatureTest(object):

    def __init__(self):
        pass  


if __name__ == "__main__":
    #gen key paire
    private_key,public_key = generate_key_pair()
    #print (SigningKey(private_key).get_verifying_key().encode().decode())
    print ("\nnode pubkey&prikey is:")
    print ("    public  key is:" + str(public_key))
    print ("    private key is:" + str(private_key))
    #sign transation
    asset = Asset(data={"bicycle": {"manufacturer":  "bkfab" ,"serial_number":  "abcd1234"}})
    metadata = {"payload":"test signature"}
    print ("\ncreate payload is:" + str(metadata))
    tx = Transaction.create([public_key], [([public_key],1)], metadata=metadata, asset=asset)
    print ("\ncreate transaction is:")
    print ("    " + str(tx.to_dict()))
    #sign transaction
    tx = tx.sign([private_key])
    print ("\nsign transaction is:")
    print ("    " + str(tx.to_dict()))
    tx_dict = tx.to_dict()
    print ("\nthe signature of transaction is:")
    print ("    " +  str(tx_dict['transaction']['fulfillments'][0]['fulfillment']))


    #sign block
    print ("\ncreate&sign block is :")
    b = Bigchain(public_key=public_key, private_key=private_key)
    block = b.create_block([tx])
    block_dict = block.to_dict()
    print ("    " + str(block_dict))
    print ("\nthe signature of block is:")
    print ("    " + str(block_dict["signature"]))
