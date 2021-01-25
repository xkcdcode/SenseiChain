import base64
import secrets
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptedSearch:

    def __init__(self):
        self.aad = b"Sensei Chain"
        with open('symmetric.key') as f:
            secret = f.read()
            f.close()
        self.secret_key = bytes.fromhex(secret)
        with open('index.key') as f:
            blind_index = f.read()
            f.close()
        self.index_key = bytes.fromhex(blind_index)

    def trace(func):
        """
        A decorator for tracing methods' begin/end execution points
        """

        def tracer(*args, **kwargs):
            name = func.__name__
            print('\tENTERING "{}"'.format(name))
            result = func(*args, **kwargs)
            print('\tLEAVING "{}"'.format(name))
            return result

        return tracer

    @trace
    def encrypt_name(self, name):
        str_to_bytes = name.encode('utf-8')
        nonce = secrets.token_bytes(nbytes=12)
        chacha = ChaCha20Poly1305(self.secret_key)
        ciphertext = chacha.encrypt(nonce, str_to_bytes, self.aad)

        return base64.urlsafe_b64encode(nonce).decode('utf-8') + "||" + base64.urlsafe_b64encode(ciphertext).decode('utf-8')

    @trace
    def decrypt_name(self, nonce_ciphertext):
        chacha = ChaCha20Poly1305(self.secret_key)
        decoded = nonce_ciphertext.split("||")
        nonce = base64.urlsafe_b64decode(decoded[0])
        ciphertext = base64.urlsafe_b64decode(decoded[1])
        plaintext = chacha.decrypt(nonce, ciphertext, self.aad)
        bytes_to_str = plaintext.decode('utf-8')
        return bytes_to_str

    @trace
    def get_name_blind_index(self, name):
        str_to_bytes = name.encode('utf-8')
        # salt = secrets.token_bytes(nbytes=16)
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=8, salt=self.index_key, iterations=1000)
        blind_index = kdf.derive(str_to_bytes)
        return base64.urlsafe_b64encode(blind_index).decode('utf-8')

    @trace
    def find_name(self, name):
        blind_index = self.get_name_blind_index(name)
        # $stmt = $db->prepare('SELECT * FROM humans WHERE ssn_bidx = ?');
        # $stmt->execute([$index]);
        result = ""
        return blind_index


if __name__ == "__main__":
    sender_name = "alice"
    receiver_name = "bob"
    se = EncryptedSearch()

    delim = "    "
    tx_data = se.get_name_blind_index(sender_name) + delim + se.encrypt_name(sender_name) + delim + se.get_name_blind_index(receiver_name) + delim \
              + se.encrypt_name(receiver_name)
    print(tx_data)
    lst_data = tx_data.split(delim)
    for item in lst_data:
        print(item)
    print(lst_data[-1])

