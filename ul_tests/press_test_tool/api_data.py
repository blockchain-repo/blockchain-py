#!/usr/bin/env python
#coding=utf-8
"""
test_data_json_body =  \
{
    "id": "16cd78bc53fc64c2bcbe8e991da1b88f57ba852c62734bcd9ea9e65b55cf75a9",
    "transaction": {
        "conditions": [
            {
                "cid": 0,
                "condition": {
                    "details": {
                        "bitmask": 32,
                        "public_key": "Bc4TEit6zNLvxnxmUqSGYTdx5T1aMifrT5dK2AiD9Lk",
                        "signature": None,
                        "type": "fulfillment",
                        "type_id": 4
                    },
                "uri": "cc:4:20:ArdzNIYG9bOxt0GLV97gfY5GSlrCC6oLiCOzZQ_PQOk:96"
            },
        "owners_after": [
          "Bc4TEit6zNLvxnxmUqSGYTdx5T1aMifrT5dK2AiD9Lk"
        ]
      }
    ],
    "data": {
      "payload": {
        "msg": "Hello BigchainDB!"
      },
      "uuid": "f5f90564-9897-493e-8d3b-1a2600bbbc4f"
    },
    "fulfillments": [
      {
        "owners_before": [
          "GcxoTqtGPTEcRguvwABHtJ6DVEBPoetBCPgi6Tw6zrDd"
        ],
        "fid": 0,
        "fulfillment": "cf:4:6BW6COlYhti0ZkgOqtPSBDyaVkEFooD29pKUSrkXELgeL-qR8wIpNgPipn1gC3HDMWG21K2kCR07HgiMp7o5XLxiHbhdVMHnpswa1L0oIkI6xxHV5h77dgyV-f1LCdAF",
        "input": None
      }
    ],
    "operation": "CREATE"
  },
  "version": 1
}
"""
test_data_json_body = {}
test_data_json_headers = {'content-type': 'application/json'}
