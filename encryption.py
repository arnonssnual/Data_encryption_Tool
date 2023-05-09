from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64

class encryption_app:

    def hashing(self,data):
        bytes_read = bytes(data,'utf-8')
        hash_object = SHA256.new()
        hash_object.update(bytes_read)
        return hash_object.hexdigest()
    

    def encrypt_RSA(self,plaintext, public_key):
        public_key = RSA.import_key(public_key)
        cipher = PKCS1_OAEP.new(public_key)
        print(plaintext)
        ciphertext = cipher.encrypt(plaintext)
        ciphertext_64 = base64.b64encode(ciphertext)
        return ciphertext_64
    
    def decrypt_RSA(self,ciphertext, private_key):
        ciphertext = base64.b64decode(ciphertext)
        private_key = RSA.import_key(private_key)
        cipher = PKCS1_OAEP.new(private_key)
        session_key = cipher.decrypt(ciphertext)
        return session_key