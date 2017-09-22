from bigchaindb import Bigchain

b = Bigchain()

res = b.gettxRecordByPubkey(pubkey="9GxFx9CueGAm37qfEDEuhrkV4Dss4yF2FVgcKd9ZCSKf", pageSize=10, pageNum=1,
                            start="1",
                            end="2")
print(res)
