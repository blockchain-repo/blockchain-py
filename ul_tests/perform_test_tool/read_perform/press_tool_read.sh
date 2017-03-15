#!/bin/bash

function usage(){
    echo -e "Usage: $0 \$1 \$2"
    echo -e "\t\t \$0 每秒发送的压力大小"
    echo -e "\t\t \$1 统计阶段前压力持续时间 s"
    echo -e "\t\t \$2 统计阶段  压力持续时间 s"
    echo -e "\t\t \$3 统计阶段后压力持续时间 s"
    return 0
}

[[ $# -lt 4 ]] && usage && exit 1


##压力大小,每秒发送的请求数
send_press=$1
##压力时间,统计阶段前的压力持续时间
send_before_range=$2
##压力时间,发送请求的持续时间
send_stat_range=$3
##压力时间,统计阶段后的压力持续时间
send_after_range=$4
send_host=192.168.0.249
send_port=40
rethinkdb_host=192.168.0.240
rethinkdb_port=28015
rethinkdb_db=bigchain
read_log="log/press_read.log"
process_log="log/press_process.log"
result_log="log/press_result.log"

mkdir -p log
rm -rf log/*.log 2>/dev/null
send_total=$(($send_press * $send_stat_range))
############################################################################
echo -e "============press param info==================" > $result_log
echo -e "press cmd  : $0" >> $result_log
echo -e "press param:"  >> $result_log
echo -e "\t\t: send_host [$send_host]"  >> $result_log
echo -e "\t\t: send_port [$send_port]"  >> $result_log
echo -e "\t\t: send_press [$send_press]"  >> $result_log
echo -e "\t\t: send_beore_state [$send_before_range], send_request[$(($send_press * $send_before_range))]"  >> $result_log
echo -e "\t\t: send_stat_range [$send_stat_range], send_request[$(($send_press * $send_stat_range))]"  >> $result_log
echo -e "\t\t: send_after_range [$send_after_range], send_request[$(($send_press * $send_after_range))]"  >> $result_log
#############################################################################

## args: $1 send_state
##       $2 send_press
##       $3 send_tx_id
function send_req_read(){
    local s_state=$1
    local s_press=$2
    local s_tx_id=$3
    local now_date=`date "+%Y-%m-%d %H:%M:%S"`
    for((i=0;i<=$s_press;i++))
    do
        now_date=`date "+%Y-%m-%d %H:%M:%S"`
        echo "[$now_date]send $s_state read a request..." >> $read_log
        if [[ $s_state == "stat" ]];then
            curl -i -H "Content-Type:application/json" -X POST -d '{"tx_id":"'${s_tx_id}'","type":"1"}' -w "{'$now_date'} %{http_code}" http://$send_host:$send_port/uniledger/v1/transaction/queryByID >> $read_log  2>&1 &
        else
            curl -i -H "Content-Type:application/json" -X POST -d '{"tx_id":"'${s_tx_id}'","type":"1"}' -w "{'$now_date'} %{http_code}" http://$send_host:$send_port/uniledger/v1/transaction/queryByID >> /dev/null  2>&1 &
        fi
    done
    return 0
}

## args: $1 s_state
##       $2 s_loop
##       $3 s_last_press
##       $4 s_tx_id
function send_req_read_for_loop(){
    local s_state=$1
    local s_loop=$2
    local s_last_press=$3
    local s_tx_id=$4
    for((i=1;i<=$s_loop;i++))
    do
        send_req_read $s_state 500 $s_tx_id &
    done
    [[ $s_last_press -ne 0 ]] && send_req_read $s_state $s_last_press &
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
    while [[ `echo "$send_end $send_begin"|awk '{if(($1-$2)<'$s_range')print 1;else print 0}'` -eq 1 ]];
    do
        ##每个发送请求只有500的容量，因此按500进行并行发送
        send_req_read_for_loop $s_state $s_loop $s_last_press $s_tx_id
        sleep 1s
        send_end=`date "+%s"`
        echo "[state:$s_state][`date "+%Y-%m-%d %H:%M:%S"`]send $s_state $send_press read request..." >> $process_log
    done 
    echo "[state:$s_state][`date "+%Y-%m-%d %H:%M:%S"`]send $s_state read request end........" >> $process_log
    return 0
}

## args: $1 send_press
function get_req_loop_info(){
    local s_press=$1
    local send_loop=$(($s_press / 500))
    local send_last_press=$(($s_press % 500))
    echo "${send_loop},${send_last_press}"
    return 0
}

function stat_read(){
    echo -e "=========before stat request press==========" >> $result_log
    cat $read_log 2>/dev/null | grep -o "\[.*\]send before read a request" |awk -F"]" '{print $1}'|sed "s/\[//g"|sort|uniq -c >> $result_log
    echo -e "=========stat request press=================" >> $result_log
    cat $read_log 2>/dev/null | grep -o "\[.*\]send stat read a request" |awk -F"]" '{print $1}'|sed "s/\[//g"|sort|uniq -c >> $result_log
    echo -e "=========after stat request press===========" >> $result_log
    cat $read_log 2>/dev/null | grep -o "\[.*\]send after read a request" |awk -F"]" '{print $1}'|sed "s/\[//g"|sort|uniq -c >> $result_log
    return 0
}

function stat_result(){
    local stat_begin_time=`grep "send stat read request begin" $process_log 2>/dev/null|awk -F"]" '{print $2}'|sed "s/\[//g"`
    local stat_end_time=`grep "send stat read request end" $process_log 2>/dev/null|awk -F"]" '{print $2}'|sed "s/\[//g"`
    [[ -z $stat_begin_time || -z $stat_end_time ]] && echo "stat_data fail[stat_begin_time or stat_end_time not exists!!!]" && return 1
    local begin_timestamp=$[$(date -d "$stat_begin_time" +%s%N)/1000000]
    local end_timestamp=$[$(date -d "$stat_end_time" +%s%N)/1000000]

    echo -e "=======state read response==================" >> $result_log
    cat $read_log 2>/dev/null |grep -o "}\[.*\] 200"|awk -F"]" '{print $1}'|sed "s/}\[//g"|sort|uniq -c >> $result_log
    echo -e "=======State Result: stat_range=============" >> $result_log
    echo -e "[stat result]stat_begin_time: $stat_begin_time, $begin_timestamp" >> $result_log
    echo -e "[stat result]stat_end_time  : $stat_end_time, $end_timestamp" >> $result_log
    local stat_timestamp_range=$(($end_timestamp - $begin_timestamp))
    stat_timestamp_range=$(($stat_timestamp_range / 1000))
    local stat_transaction_sum=`cat $read_log 2>/dev/null | grep "}\{.*\} 200"|wc -l`
    local stat_transaction_avg=$(($stat_transaction_sum / $stat_timestamp_range))
    echo -e "[stat result]stat_transaction_sum: $stat_transaction_sum" >> $result_log
    echo -e "[stat result]stat_timestamp_range: $stat_timestamp_range" >> $result_log
    echo -e "[stat result]TPS: $stat_transaction_avg" >> $result_log

    return 0
}
##############################################################################
read_transaction_id=`python3 get_transactionid.py`
[[ -z $read_transaction_id ]] && echo "get_one_transactionid fail!!!" && exit 1
read_transaction_id="d0e9a4dd947dd0284c087b302a3b9783de4e2ebd839df579177799a5ccee925e"
send_read "before" $send_before_range $read_transaction_id 
wait
send_read "stat" $send_stat_range $read_transaction_id 
wait
send_read "after" $send_after_range $read_transaction_id 
wait
echo -e "============read request stat==================" >> $result_log
stat_read

stat_result

exit 0
