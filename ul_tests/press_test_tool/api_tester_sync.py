#!/usr/bin/env python
#coding=utf-8

import http.client
import urllib
import logging
import json
import random
import os
import sys
import time
import threading
import uuid
from api_conf import *
from api_data import *

os.system("mkdir -p ./log")
global log_file_path,log_file_name
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s%(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S ',
                    filename="%s/%s" % (log_file_path, log_file_name),
                    filemode='w')

def do_work():
    global api_host
    global api_port
    global api_method
    global api_url
    global api_full_url
    global test_data_json_body
    global test_data_json_headers
    global test_error_num
    httpClient = None
    try:
        str_test_data_json_body = json.dumps(test_data_json_body)
        httpClient = http.client.HTTPConnection(api_host, int(api_port), timeout=10)
        httpClient.request(api_method, api_url, str_test_data_json_body, test_data_json_headers)
        response = httpClient.getresponse()
        response_status = str(response.status)
        log_str = '[request] api_full_url: ' + api_full_url + \
                  '[response] status: ' + str(response_status)
        if response_status and str(response_status) == "200":
            log_str = "%s; request success." % (log_str)
        else:
            log_str = "%s; request fail!" % (log_str)
            test_error_num += 1
        logging.warning(log_str)
    except Exception as e:
        logging.error(str(e))
        test_error_num += 1
    finally:
        if httpClient:
            httpClient.close()

def working():
    global test_request_thread_per_senonds
    global test_conf_press_time
    idx_w = 0
    while idx_w < (test_request_thread_per_senonds * test_conf_press_time):
        idx_w += 1
        do_work()

def main():
    global test_conf_thread_num
    global test_conf_press_per_secones
    global test_request_thread_per_senonds
    global test_conf_press_time
    global test_request_tatal_num
    global test_error_num
    global test_request_interval
    threads = []
    t1 = time.time()
    for i in range(test_conf_thread_num):
        t = threading.Thread(target=working, name="T"+str(i))
        t.setDaemon(True)
        threads.append(t)
        #time.sleep(test_request_interval)         
    for t in threads:
        t.start()
    for t in threads:
        t.join()
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
