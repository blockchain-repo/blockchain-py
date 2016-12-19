
import rapidjson
import zlib



# each line is a node's ip
def read_nodes(nodes_file):
    nodes_list = []
    nodes = open(nodes_file)
    for line in nodes.readlines():
        nodes_list.append(line.strip('\n'))
    return nodes_list


# convert queue to list
def convert_to_list(received):
    re = []
    while received.qsize() > 0:
        re.append(received.get())
    return re


def decode_data(data, compress=False, charset="utf-8", show=True):
    """
    Args:
       data: json str data compress or json str[compress=False]
       compress: if True, compress the data
       charset: decode
       show: if True, show the compress info
    Return:
        json obj
   """

    if data:
        if compress:
            decompress_data = zlib.decompress(data)
            data_json_str = decompress_data.decode(charset)
            data_json_obj = rapidjson.loads(data_json_str)
            if show:
                ################################# compress info ###################################
                ratio = "%.2f%%" % (len(data) / len(decompress_data) * 100)
                print("Received message, size={:<10}, decompress size={:<10},compression ratio={:<8}"
                      .format(len(data), len(decompress_data), ratio))
                ################################# compress info ###################################
        else:
            data_json_str = data.decode(charset)
            data_json_obj = rapidjson.loads(data_json_str)
            if show:
                ################################# compress info ###################################
                print("Received message, size={}"
                      .format(len(data)))
                ################################# compress info ###################################
        if data_json_obj == "null":
            data_json_obj = None
        return data_json_obj


def encode_data(data, compress=False, encoding="utf8", show=True):
    """
    Args:
        data: json obj data
        compress: if True, compress the data
        encoding: encode
        show: if True, show the compress info
    Return:
        bytes str or json str[compress=False]
    """

    if data:
        if compress:
            data = rapidjson.dumps(data)
            response_data_bytes = bytes(data, encoding=encoding)
            response_data = zlib.compress(response_data_bytes, zlib.Z_BEST_COMPRESSION)
            if show:
                ################################# compress info ###################################
                ratio = "%.2f%%" % (len(response_data) / len(data) * 100)
                print("Send message, size={:<10}, decompress size={:<10},compression ratio={:<8}"
                      .format(len(data), len(response_data), ratio))
                ################################# compress info ###################################
            return response_data
        else:
            return data


def deal_response(data, make_response, compress=False):
    """
    Args:
        data: json obj data
        make_response: flask force modify the current response header type
        compress: if True, compress the data and set the header with stream
    Return:
        bytes str or json str[compress=False]
    """

    if data:
        if compress:
            result = encode_data(data=data,compress=True)
            result = make_response(result)
            result.headers['Content-Type'] = "application/octet-stream"
        else:
            result = encode_data(data=data,compress=False)
        return result