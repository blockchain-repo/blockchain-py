from uuid import uuid4
from bigchaindb.common.crypto import generate_key_pair
from bigchaindb.common.crypto import SigningKey, VerifyingKey
import time

pri, pub = generate_key_pair()
signing_key = SigningKey(pri)
verifying_key = VerifyingKey(pub)

msg = str(uuid4())
times = 1000
start = time.time()
print("start", start)
for a in range(times):
    signature = signing_key.sign(msg.encode()).decode()
    # result = verifying_key.verify(msg.encode(), signature)
end = time.time()
print("end", end)
print("takes", end - start, "seconds")
print("sign", times / (end - start), "times/s")
