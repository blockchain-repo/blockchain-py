#!/bin/bash

process_log=$1

cat $1 |grep "Requests per second"|awk -F":" '{print $2}'|awk '{print $1}'|awk -F"." '{print $1}' >  ./log/request.log

request_sum=`cat ./log/request.log |awk 'BEGIN{sum=0}{sum=sum+$1}END{print sum}'`
request_num=`wc -l ./log/request.log|awk '{print $1}'`
echo $(($request_sum / $request_num))
