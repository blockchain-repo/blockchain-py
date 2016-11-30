#!/usr/bin/env python
#coding=utf-8

###api url configure
test_flag = False
api_host = "36.110.115.195"
api_port = "39"
api_method = "POST"
#api_method = "GET"
if not test_flag:
    api_url = "/api/v1/transactions/test"
else:
    api_url = ""
api_full_url = "http://%s:%s%s" % (api_host, api_port, api_url)

###api press param configure
test_conf_press_time = 2
test_conf_thread_num = 10
test_conf_press_per_secones = 3
test_request_thread_per_senonds = test_conf_press_per_secones/test_conf_thread_num
test_request_tatal_num = test_conf_press_per_secones * test_conf_press_time
test_request_interval = 1.0/test_conf_press_per_secones
test_error_num = 0

###api log configure
log_file_path = "./log"
log_file_name = "api_tester.log"
