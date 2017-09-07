from uuid import uuid4
from bigchaindb.common.crypto import generate_key_pair
from bigchaindb.common.crypto import SigningKey, VerifyingKey

pri, pub = generate_key_pair()
print("===generate_key_pair===")
print("pri:", pri, "\npub:", pub)
print("===create_random_msg===")
msg = str(uuid4())
print(msg)
print("===sign_msg_with_pri===")
signing_key = SigningKey(pri)
signature = signing_key.sign(msg.encode()).decode()
print(signature)
print("===verify_sig_with_pub===")
verifying_key = VerifyingKey(pub)
result = verifying_key.verify(msg.encode(), signature)
print(result)
