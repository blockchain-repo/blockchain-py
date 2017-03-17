import base64
import os
from Crypto.Cipher import AES


class AESCipher(object):

    def __init__(self, key):
        self.bs = 32
        # self.key = hashlib.sha256(key.encode()).digest()
        self.key = key


    def encrypt(self, raw):
        raw = self._pad(raw)
        # print("insert raw is {}".format(raw))
        iv = os.urandom(AES.block_size)
        # iv = Random.get_random_bytes(AES.block_size)
        # iv = Random.new().read(AES.block_size)
        # iv = bytes(self.key, encoding="utf-8")
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        # print("decrypt ... enc {}".format(enc))
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

if __name__ == '__main__':
    # 密钥长度可以为128 / 192 / 256比特，这里采用128比特
    # 指定加密模式为CBC
    key = "unichain12345678unichain12345678"
    demo = AESCipher(key)
    text = "unichain12345678unichain1\n2345678unichain12345678uqerii#!@)*&#)!hljd" \
           "\n\nq~|{@\sauiwenichain12345678unicha\nin12345678unichain12345678unichain12345678" \
           "unichain12345678unichain123456\n78unichain12345678unichain12345678" \
           "unichain12345678" \
           "unichain12345678" \
           "unichain12345678" \
           "unichain12345678" \
           "unichain12345678123@\nwwww234@#)()()*()_)(_(+JLKJLKDHSLKDJ" \
           "z09793048231!)@*!@_#_!@U$()!&@_($!@}{{J!H:G#F!K@GHIK#ISHF!24123312"

    e = demo.encrypt(text)
    d = demo.decrypt(e)

    print("encrypt: len={}, \n{}".format(len(e), e))
    print("decrypt: len={}, \n{}".format(len(d), d))