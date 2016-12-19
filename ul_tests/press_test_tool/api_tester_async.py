#!/usr/bin/env python
#coding=utf-8
import http.client
import logging
import json
import time
import threading
import queue
import os
from api_conf import *
from api_data import *
"""
import logging.config
import codecs
import yaml
logging.config.dictConfig(codecs.open("cfg/logger.yml",'r','utf-8').read())
logger = logging.getLogger("infologgerfile")
"""
os.system("mkdir -p ./log")
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s%(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S ',
                    filename="%s/%s" % (log_file_path, log_file_name),
                    filemode='w')

class Worker(threading.Thread):
    def __init__(self, workQueue, resultQueue, **kwds):
        threading.Thread.__init__(self, **kwds)
        self.setDaemon(True)
        self.workQueue = workQueue
        self.resultQueue = resultQueue

    def run(self):
        while 1:
            try:
                callable, args, kwds = self.workQueue.get(False)
                res = callable(*args, **kwds)
                self.resultQueue.put(res)
            except queue.Empty:
                break

class WorkManager:
    def __init__(self, num_of_workers=10):
        self.workQueue = queue.Queue()
        self.resultQueue = queue.Queue()
        self.workers = []
        self._recruitThreads(num_of_workers)

    def _recruitThreads(self, num_of_workers):
        for i in range(num_of_workers):
            worker = Worker(self.workQueue, self.resultQueue)
            self.workers.append(worker)

    def start(self):
        for w in self.workers:
            w.start()

    def wait_for_complete(self):
        while len(self.workers):
            worker = self.workers.pop()
            worker.join()
            if worker.isAlive() and not self.workQueue.empty():
                self.workers.append(worker)
        logging.info("all requests were sended completely!!")

    def add_job(self, callable, *args, **kwds):
        self.workQueue.put((callable, args, kwds))

    def get_result(self, *args, **kwds):
        return self.resultQueue.get(*args, **kwds)

def api_request_work():
    global test_data_json_body
    global test_data_json_headers
    global api_host
    global api_port
    global api_method
    global api_url
    httpClient = None
    response = None
    try:
        str_test_data_json_body = json.dumps(test_data_json_body)
        httpClient = http.client.HTTPConnection(api_host, int(api_port), timeout=10)
        httpClient.request(api_method, api_url, str_test_data_json_body, test_data_json_headers)
        response = httpClient.getresponse()
    except Exception as e:
        logging.error(str(e))
    finally:
        if httpClient:
            httpClient.close()
    return response

def api_reponse_work(response):
    global api_full_url
    global test_error_num
    response_status = "200"
    if not response:
        response_status = "500"
    else:
        response_status = str(response.status)
    log_str = '[request] api_full_url: ' + api_full_url + ', [response] status: ' + str(response_status)
    if response_status and str(response_status) == "200":
        log_str = "%s; request success." % (log_str)
    else:
        log_str = "%s; request fail!" % (log_str)
        test_error_num += 1
    logging.warning(log_str)

def main():
    global test_conf_thread_num
    global test_conf_press_per_secones
    global test_request_thread_per_senonds
    global test_conf_press_time
    global test_request_tatal_num
    global test_error_num
    global test_request_interval
    t1 = time.time()
    wm = WorkManager(test_conf_thread_num)
    for i in range(test_request_tatal_num):
        wm.add_job(api_request_work)

        time.sleep(test_request_interval)
        logging.info("[send request]request %d is sent!!!" % (i))
    wm.start()
    wm.wait_for_complete()
    for i in range(test_request_tatal_num):
        response = wm.get_result()
        api_reponse_work(response)
    t2 = time.time()

    print ("========================================")
    print ("URL:%s"%(api_full_url))
    print ("任务数量:",test_conf_press_per_secones,"*",test_conf_press_time,"=",test_request_tatal_num)
    print ("总耗时(秒):",t2-t1)
    print ("每次请求耗时(秒):",(t2-t1)/(test_request_tatal_num))
    print ("每秒承载请求数:",1/((t2-t1)/(test_request_tatal_num)))
    print ("请求成功数量任务量 ：", test_request_tatal_num-test_error_num, "  请求失败任务量", test_error_num)

if __name__=='__main__':
    main()
