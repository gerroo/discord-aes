#INFO: Crypto module will be multithreaded (another thread)
#INFO: GNUPG-py docs -> https://pythonhosted.org/python-gnupg/
#INFO: We will use base 64 encoding as our mock encoding



import re
import base64
from Crypto.Cipher import AES
# assumed to be a CSPRNG
from Crypto import Random
import hashlib


HASH_BEGIN = '-----BEGIN HASH-----'
HASH_END = '-----END HASH-----'

AES_BEGIN = '-----BEGIN CIPHERTEXT-----'
AES_END = '-----END CIPHERTEXT-----'


BS_AES = 32
pad_aes = lambda s: s + (BS_AES - len(s) % BS_AES) * chr(BS_AES - len(s) % BS_AES)
unpad_aes = lambda s : s[0:-(s[-1])]


revchnk = lambda s, n: s and revchnk(s[n:], n) + s[:n]


def gen_aes_key(password, salt, iterations):
    assert iterations > 0
    key = bytearray(password, 'utf-8') + salt
    for i in range(iterations):
        key = hashlib.sha256(key).digest()
    return key


class AesCipher:

    def __init__(self, iter_count=16384, salt_len=16):
        self.iter_count = iter_count
        self.salt_len = salt_len


    def _encrypt_raw(self, plain: str, password: str):
        plain = pad_aes(plain)

        iv = Random.new().read(AES.block_size)
        salt = Random.new().read(self.salt_len)

        key = gen_aes_key(password, salt, self.iter_count)

        cipher = AES.new(key, AES.MODE_CBC, iv)
        return base64.b85encode(iv + salt + cipher.encrypt(plain)).decode('utf-8')


    def _decrypt_raw(self, enced: str, password: str):
        enced = base64.b85decode(bytearray(enced, 'utf-8'))

        iv = enced[:AES.block_size]
        salt = enced[AES.block_size: AES.block_size + self.salt_len]

        key = gen_aes_key(password, salt, self.iter_count)

        cipher = AES.new(key, AES.MODE_CBC, iv)
        return unpad_aes(cipher.decrypt(enced[AES.block_size + self.salt_len:])).decode('utf-8')


    def aes_encrypt(self, plain: str, password: str):
        potato = revchnk(hashlib.sha256(password.encode('utf-8')).hexdigest(), 2)
        return HASH_BEGIN + potato + HASH_END + AES_BEGIN + self._encrypt_raw(plain, password) + AES_END


    def aes_decrypt(self, enced: str, password: str):
        potato = revchnk(hashlib.sha256(password.encode('utf-8')).hexdigest(), 2)
        delim = HASH_BEGIN + '(.*?)' + HASH_END
        if potato in re.findall(delim, enced, re.S):
            isol = re.findall(AES_BEGIN + '(.*?)' + AES_END, enced, re.S)[0]
            return self._decrypt_raw(isol, password)
        else:
            return None
class keys:
    keys = {}
    AesCipher = AesCipher()

    def addKey(owner:str ,key:str):
        keys[owner] = key
        return 1

    def getKey(owner):
        try:
            a = keys[owner]
        except:
            dbg_print("Key doesn't exist.")
        return a

    def save(file, password="defaultpassword"):
        filestr = ""
        for i in self.keys.keys():
            filestr += f"{f}->{self.keys[i]}\n"

        filestr_encrypted = AesCipher.aes_encrypt(filestr, password)
        f = open(file,"w")
        f.write(filestr_encrypted)
        f.close()
        return 1

    def open(file, password="defaultpassword"):
        f = open(file, "r")
        filestr_encrypted = f.read()
        f.close()
        filestr = AesCipher.aes_decrypt(filestr_encrypted, password).split("\n")
        for i in filestr:
            owner, key = i.split("->")
            keys[owner] = key
        return 1

    def open_raw(file, password="defaultpassword"):
        f = open(file, "r")
        filestr = f.read()
        f.close()
        for i in filestr:
            owner, key = i.split("->")
            keys[owner] = key
        return 1
