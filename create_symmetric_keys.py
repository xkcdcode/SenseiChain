import secrets

# with open('symmetric.key', 'w') as f:
#     f.write(secrets.token_hex(32))
#     f.close()

with open('index.key', 'w') as f:
    f.write(secrets.token_hex(16))
    f.close()

# data = b"a secret message"
# aad = b"authenticated but unencrypted data"
# secret_key = secrets.token_hex(32)
# key = bytes.fromhex(secret_key)
# print(key)
# print(type(key))
# print(len(key))
# chacha = ChaCha20Poly1305(key)
# nonce = secrets.token_bytes(nbytes=12)
# ct = chacha.encrypt(nonce, data, aad)
# res = chacha.decrypt(nonce, ct, aad)
# print(res)
