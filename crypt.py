import hashlib
from Crypto import Random
from Crypto.Cipher import AES


class AESCipher:

    def __init__(self, key): 
        self.bs = 32	# Block size
        self.key = hashlib.sha256(key.encode()).digest()	# 32 bit digest

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(raw)

    def decrypt(self, enc):
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:]))

    def _pad(self, s):
         return s + bytes([self.bs - len(s) % self.bs] * (self.bs - len(s) % self.bs))

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]
