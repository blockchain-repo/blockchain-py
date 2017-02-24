from bigchaindb.common.util import gen_timestamp
import time
import datetime

class GenTimestampTest(object):

    def get_now_timestamp(self):
        return gen_timestamp()


if __name__ == "__main__":
    testcase = GenTimestampTest()
    print ("Get Now Timestamp:")
    print ("    Now Time : " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))) 
    print ("    Timestamp: " + testcase.get_now_timestamp())
