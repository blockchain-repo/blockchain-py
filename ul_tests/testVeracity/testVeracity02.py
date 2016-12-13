import requests
import random
import time
import sys
import multiprocessing as mp
import os
import uuid
import json
# post test


processCount = sys.argv[1]

url = 'http://127.0.0.1:9984/testVeracity_api/v1/createtxBypayload/'
headers = {'content-type': 'application/json'}


def startRun():
    postpid = os.getpid()
    postcount = 0
    while True:
        random_transactions = random.Random().randint(500, 999)
        sleep_random = random.Random().randint(1, 4)
        print('will create %d transactions and then sleep %ds' % (random_transactions, sleep_random))
        # starttimefor = datetime.datetime.now().microsecond
        for i in range(random_transactions):

            try:
                # time.sleep(0.4)
                data = {
                    "uuid": str(uuid.uuid4())
                }
                payload = json.dumps(data)

                postcount = postcount+1
                res = requests.post(url, data=payload, headers=headers)
                print("code:%d .. %d has send %d posts" % (res.status_code,postpid,postcount))
            except Exception as e:
                print(e)
                print("%d has send %d posts" % (postpid,postcount))
                # print("post except!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # endtimefor = datetime.datetime.now().microsecond
        # print('cost %d ms create %d transactions' % ((endtimefor-starttimefor)/1000,random_transactions))
        time.sleep(sleep_random)


if __name__ == "__main__":
    pool = mp.Pool(processes=int(processCount))
    for i in range(int(processCount)):
        result = pool.apply_async(startRun)
    pool.close()
    pool.join()
    print(result.successful())