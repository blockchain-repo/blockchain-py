#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 3/16/17 11:02 PM
# @Author  : XIN WANG
# @Site    : https://github.com/wxcsdb88
# @Software: PyCharm Community Edition


from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
# from Crypto import Random
import base64

# padding算法
BS = AES.block_size # aes数据分组长度为128 bit
pad = lambda s: s + (BS - len(s) % BS) * chr(0)


class aesdemo:
    def __init__(self, key, mode, iv):
        self.key = key
        self.mode = mode
        self.iv = iv

    def encrypt(self, plaintext):
        # 生成随机初始向量IV
        # iv = Random.new().read(AES.block_size)
        cryptor = AES.new(self.key, self.mode, self.iv)
        ciphertext = cryptor.encrypt(pad(plaintext))
        # 这里统一把加密后的字符串转化为16进制字符串
        # 在下节介绍base64时解释原因
        return b2a_hex(self.iv + ciphertext)

    def decrypt(self, ciphertext):
        ciphertext = a2b_hex(ciphertext)
        # iv = ciphertext[0:AES.block_size]
        ciphertext = ciphertext[AES.block_size:len(ciphertext)]
        cryptor = AES.new(self.key, self.mode, self.iv)
        plaintext = cryptor.decrypt(ciphertext)
        return plaintext.rstrip(chr(0))

    def encrypt_base64(self, plaintext):
        # 生成随机初始向量IV
        # iv = Random.new().read(AES.block_size)
        cryptor = AES.new(self.key, self.mode, self.iv)
        ciphertext = cryptor.encrypt(pad(plaintext))
        return base64.encodestring(self.iv + ciphertext)

    def decrypt_base64(self, ciphertext):
        ciphertext = base64.decodestring(ciphertext)
        # iv = ciphertext[0:AES.block_size]
        ciphertext = ciphertext[AES.block_size:len(ciphertext)]
        cryptor = AES.new(self.key, self.mode, self.iv)
        plaintext = cryptor.decrypt(ciphertext)
        return plaintext.rstrip(chr(0))


# 测试模块
if __name__ == '__main__':
    # 密钥长度可以为128 / 192 / 256比特，这里采用128比特
    # 指定加密模式为CBC
    key = "unichain12345678"
    iv = "12345678!@#$%^&*"
    demo = aesdemo(key, AES.MODE_CBC, iv)
    import sys
    text = "daer jlaodfkl了；了；地方；爱离开饭店；挨饿日寇；大姐夫啊；人；快乐（）80940724；咯9874&）×……×（）×）8234"
    e = demo.encrypt(text)
    d = demo.decrypt(e)
    e1 = demo.encrypt_base64(text)
    d1 = demo.decrypt_base64(e1)

    print("encrypt: len={}, \n{}".format(len(e), e))
    print("decrypt: len={}, \n{}".format(len(d), d))
    print("encrypt_base64: len={}, \n{}".format(len(e1), e1))
    print("decrypt_base64: len={}, \n{}".format(len(d1), d1))
