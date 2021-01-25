import secrets

secret_key = secrets.token_hex(128)
print(secret_key)

with open('secret.key', 'w') as f:
    f.write(secret_key)
    f.close()
