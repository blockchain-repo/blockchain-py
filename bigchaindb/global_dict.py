import os


def _init():#初始化
    global _global_dict
    _global_dict = {}

def set_value(key,value):
    """ 定义一个全局变量 """
    # global _global_dict
    _global_dict[key] = value

def get_value(key,defValue=None):
    """ 获得一个全局变量,不存在则返回默认值 """
    # global _global_dict
    try:
        print(' global_dict get_value 1 id ::', id(_global_dict))
        print(os.getpid(),' global_dict get_value 2 id ::', id(_global_dict[key]),'--',key)
        return _global_dict[key]
    except KeyError:
        return defValue
