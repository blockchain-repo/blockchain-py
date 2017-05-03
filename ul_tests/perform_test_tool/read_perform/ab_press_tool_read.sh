#!/bin/bash

function usage(){
    echo -e "Usage: $0 \$1 \$2"
    echo -e "\t\t \$0 每秒发送的压力大小"
    echo -e "\t\t \$2 统计阶段  压力持续时间 s"
    return 0
}

[[ $# -lt 2 ]] && usage && exit 1


#============================命令参数识别区=====================================#
##压力大小,每秒发送的请求数
send_press=$1
##压力时间,发送请求的持续时间
send_stat_range=$2
#============================可配参数配置区=====================================#
send_host=192.168.0.249
send_port=40
send_method=POST
send_content_type=application/json
send_url=/uniledger/v1/transaction/queryByID
#============================可配参数配置区=====================================#
##API host & port
rethinkdb_host=192.168.0.240
rethinkdb_port=28015
rethinkdb_db=bigchain

##生成的log路径&名称
read_thread_num=300
read_thread_log="log/press_read_thread"
##读过程日志
read_log="log/press_read.log"
##压力过程处理日志
process_log="log/press_process.log"
##性能结果分析日志
result_log="log/press_result.log"

mkdir -p log
rm -rf log/* 2>/dev/null
send_total=$(($send_press * $send_stat_range))
############################################################################
echo -e "============press param info==================" > $result_log
echo -e "press cmd  : $0" >> $result_log
echo -e "press param:"  >> $result_log
echo -e "\t\t: send_host [$send_host]"  >> $result_log
echo -e "\t\t: send_port [$send_port]"  >> $result_log
echo -e "\t\t: send_press [$send_press]"  >> $result_log
echo -e "\t\t: send_stat_range [$send_stat_range], send_request[$(($send_press * $send_stat_range))]"  >> $result_log
#############################################################################

## args: $1 send_state
##       $2 send_press
##       $3 send_tx_id
##       $4 out_file
function send_req_read(){
    local s_state=$1
    local s_press=$2
    local s_tx_id=$3
    local out_file=$4
    local now_date=`date "+%Y-%m-%d %H:%M:%S"`
    for((i=0;i<=$s_press;i++))
    do
        now_date=`date "+%Y-%m-%d %H:%M:%S"`
        #echo "[$now_date]send $s_state read a request..." >> $out_file
        if [[ $s_state == "stat" ]];then
            #curl -i -H "Content-Type:application/json" -X POST -d '{"tx_id":"'${s_tx_id}'","type":"1"}' -w "['$now_date'] %{http_code}\n" http://$send_host:$send_port/uniledger/v1/transaction/queryByID >> $out_file  2>/dev/null  &
            curl -i -H "Content-Type:application/json" -X POST -d '{"tx_id":"'${s_tx_id}'","type":"1"}' -w "['$now_date'] %{http_code}\n" http://$send_host:$send_port/uniledger/v1/transaction/queryByID  2>/dev/null  &
        else
            curl -i -H "Content-Type:application/json" -X POST -d '{"tx_id":"'${s_tx_id}'","type":"1"}' -w "['$now_date'] %{http_code}\n" http://$send_host:$send_port/uniledger/v1/transaction/queryByID >> /dev/null  2>&1 &
        fi
    done
    return 0
}

## args: $1 s_state
##       $2 s_loop
##       $3 s_last_press
##       $4 s_tx_id
##       $5 out_file
function send_req_read_for_loop(){
    local s_state=$1
    local s_loop=$2
    local s_last_press=$3
    local s_tx_id=$4
    local out_file=$5
    for((i=1;i<=$s_loop;i++))
    do
        send_req_read $s_state ${read_thread_num} $s_tx_id $out_file  &
    done
    [[ $s_last_press -ne 0 ]] && send_req_read $s_state $s_last_press $s_tx_id $out_file &
    return 0
}

## arge: $1 send_state_decription
##       $2 send_stat_range
##       $3 send_read_transaction_id
function send_read(){
    local s_state=$1
    local s_range=$2
    local s_tx_id=$3
    local s_loop_info=`get_req_loop_info $send_press`
    local s_loop=`echo "$s_loop_info"|awk -F"," '{print $1}'`
    local s_last_press=`echo "$s_loop_info"|awk -F"," '{print $2}'`
    echo "[state:$s_state][`date "+%Y-%m-%d %H:%M:%S"`]send $s_state read request begin........" >> $process_log
    local send_begin=`date "+%s"`
    local send_end=`date "+%s"`
    local default_out_file=$read_thread_log
    local idx=0
    while [[ `echo "$send_end $send_begin"|awk '{if(($1-$2)<'$s_range')print 1;else print 0}'` -eq 1 ]];
    do
        ab -r -n $send_press -c 50 -t 1 -v 2 -T "${send_content_type}" -p 'read_json.txt' 'http://'${send_host}':'${send_port}${send_url} >> $process_log 2>&1
        send_end=`date "+%s"`
        echo "[state:$s_state][`date "+%Y-%m-%d %H:%M:%S"`]send $s_state $send_press request..." >> $process_log
    done
    #while [[ `echo "$send_end $send_begin"|awk '{if(($1-$2)<'$s_range')print 1;else print 0}'` -eq 1 ]];
    #do
    #    idx=$[$idx+1]
    #    ##每个发送请求只有500的容量，因此按500进行并行发送
    #    send_req_read_for_loop $s_state $s_loop $s_last_press $s_tx_id ${default_out_file}"_"${idx}
    #    sleep 1s
    #    send_end=`date "+%s"`
    #    echo "[state:$s_state][`date "+%Y-%m-%d %H:%M:%S"`]send $s_state $send_press read request..." >> $process_log
    #done 
    echo "[state:$s_state][`date "+%Y-%m-%d %H:%M:%S"`]send $s_state read request end........" >> $process_log
    return 0
}

## args: $1 send_press
function get_req_loop_info(){
    local s_press=$1
    local send_loop=$(($s_press / ${read_thread_num}))
    local send_last_press=$(($s_press % ${read_thread_num}))
    echo "${send_loop},${send_last_press}"
    return 0
}

function stat_read(){
    local s_file=$1
    cat $s_file 2>/dev/null | grep "send stat read a request" |awk -F"]" '{print $1}'|sed "s/\[//g"|sort|uniq -c >> $result_log
    return 0
}

function stat_response(){
    local s_file=$1
    cat $s_file 2>/dev/null |grep -o "}\[.*\] 200"|awk -F"]" '{print $1}'|sed "s/}\[//g"|sort|uniq -c >> $result_log
    return 0
}

function stat_result(){
    local stat_begin_time=`grep "send stat read request begin" $process_log 2>/dev/null|awk -F"]" '{print $2}'|sed "s/\[//g"`
    local stat_end_time=`grep "send stat read request end" $process_log 2>/dev/null|awk -F"]" '{print $2}'|sed "s/\[//g"`
    [[ -z $stat_begin_time || -z $stat_end_time ]] && echo "stat_data fail[stat_begin_time or stat_end_time not exists!!!]" && return 1
    local begin_timestamp=$[$(date -d "$stat_begin_time" +%s%N)/1000000]
    local end_timestamp=$[$(date -d "$stat_end_time" +%s%N)/1000000]

    echo -e "=======State Result: stat_range=============" >> $result_log
    echo -e "[stat result]stat_begin_time: $stat_begin_time, $begin_timestamp" >> $result_log
    echo -e "[stat result]stat_end_time  : $stat_end_time, $end_timestamp" >> $result_log
    local stat_timestamp_range=$(($end_timestamp - $begin_timestamp))
    stat_timestamp_range=$(($stat_timestamp_range / 1000))
    local stat_transaction_sum=`cat $read_log 2>/dev/null | grep "}\[.*\] 200"|wc -l`
    local stat_transaction_avg=$(($stat_transaction_sum / $stat_timestamp_range))
    echo -e "[stat result]stat_transaction_sum: $stat_transaction_sum" >> $result_log
    echo -e "[stat result]stat_timestamp_range: $stat_timestamp_range" >> $result_log
    echo -e "[stat result]TPS: $stat_transaction_avg" >> $result_log

    return 0
}
##############################################################################
read_transaction_id=`python3 get_transactionid.py`
[[ -z $read_transaction_id ]] && echo "get_one_transactionid fail!!!" && exit 1
#read_transaction_id="87567a1c61a559b4d878b234d42aba0302b7f527ff3f2f88aebf86c9a74a4e22"
send_read "stat" $send_stat_range $read_transaction_id  &
wait
#for tmp_read_file in `ls ./log|grep "press_read_thread"`
#do
#    cat ./log/$tmp_read_file >> $read_log
#done
echo -e "\n===============================================" >> $result_log
echo -e "============read request stat==================" >> $result_log
echo -e "===============================================" >> $result_log
stat_read 
echo -e "\n===============================================" >> $result_log
echo -e "============read response stat=================" >> $result_log
echo -e "===============================================" >> $result_log
stat_response

echo -e "\n===============================================" >> $result_log
echo -e "============final result statt=================" >> $result_log
echo -e "===============================================" >> $result_log
stat_result

exit 0
