#!/bin/bash

function usage
{
echo -e "
Usage: $0 -h xx -p xx -m xx -u xx [-f xx |-s xx]
\t -h host
\t -p port
\t -m request method,POST|GET
\t -u api url path
\t -f file path, json from file
\t -s json string, json from string
"
return 0
}

while getopts ":h:p:m:u:f:s:a:" opt
do
    case $opt in
        h)
            API_HOST="$OPTARG"
        ;;
        p) 
            API_PORT="$OPTARG"
        ;;
        m)
            API_METHOD="$OPTARG"
        ;;
        u)
            API_APPEND_URL_FIR="$OPTARG"
        ;;
        f) 
            API_JSON_FILE="$OPTARG"
        ;;
        s)
            API_JSON_STR="$OPTARG"
        ;;
        a)
            API_APPEND_URL_SEC="$OPTARG"
        ;;
    esac  
done
##check param
if [ -z $API_HOST -o -z $API_PORT ];then
    echo "[ERROR]need host & port"
    usage
    exit 1
fi
if [ ! -z $API_JSON_FILE ];then
    if [ ! -s $API_JSON_FILE ];then
        echo "[ERROR]param -f not exist, need -f api_json_file"
        exit 1
    else
        cat $API_JSON_FILE|./JSON >/dev/null 2>&1
        [ $? -ne 0 ] && {
            echo "[ERROR]json format error, json from file[$API_JSON_FILE]"
            exit 1
        }  
    fi
fi
if [ ! -z $API_JSON_STR ];then
    echo $API_JSON_STR|./JSON >/dev/null 2>&1
    [ $? -ne 0 ] && {
        echo "[ERROR]json format error, json from str"
        exit 1
    }
fi
##do process
BASE_PATH="http://${API_HOST}:${API_PORT}"
API_BASE_PATH="${BASE_PATH}/api/v1"

if [ -z "`curl -s -i $BASE_PATH|grep -o "^HTTP/.* 200 OK"`" ];then
    echo "[ERROR]api server not OK!!!"
    exit 1
else
   API_BASE_PATH=`curl -s -i $BASE_PATH|grep "\"api_endpoint\":.*"|cut -d":" -f2-|sed "s/\"\|,\| //g"|sed "s#http:\/\/.*:[0-9]*#${BASE_PATH}#g" ` 
fi

API_CMD="curl -s -i"
API_APPEND_STR=" "
API_URL=${API_BASE_PATH}

if [ ! -z $API_METHOD ];then
    API_APPEND_STR=${API_APPEND_STR}"-X $API_METHOD "
fi

if [ ! -z $API_APPEND_URL_FIR ];then
    API_URL=${API_URL}"/${API_APPEND_URL_FIR}"
    API_URL=`echo -e ${API_URL}|sed "s/\/\//\//g"`
fi

if [ ! -z $API_APPEND_URL_SEC ];then
    API_URL=${API_URL}"/${API_APPEND_URL_SEC}"
    API_URL=`echo -e ${API_URL}|sed "s/\/\//\//g"`
fi

if [ ! -z $API_JSON_FILE ];then
    API_APPEND_STR=${API_APPEND_STR}"-H 'Content-Type:application/json' -d \'`cat ${API_JSON_FILE}|./JSON|grep "^\[\]"|cut -f2`\' "
fi

if [ ! -z $API_JSON_STR ];then
    API_APPEND_STR=${API_APPEND_STR}"-H 'Content-Type:application/json' -d \'${API_JSON_STR}\' "
fi

API_URL=`echo -e ${API_URL}|sed "s/:\//:\/\//g"`
API_FINAL_CMD=${API_CMD}${API_APPEND_STR}${API_URL}
echo "[API CMD]"$API_FINAL_CMD

eval $API_FINAL_CMD

exit 0
