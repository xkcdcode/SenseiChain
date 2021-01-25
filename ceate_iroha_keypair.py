from iroha import IrohaCrypto


hsbc_private_key = IrohaCrypto.private_key()
hsbc_public_key = IrohaCrypto.derive_public_key(hsbc_private_key)

with open('hsbc.pri', 'w') as f:
    f.write(hsbc_private_key.hex())
    f.close()

with open('hsbc.pub', 'w') as f:
    f.write(hsbc_public_key.hex())
    f.close()

# with open('hsbc.pub') as f:
#     key = f.read()
#     f.close()
#
# pub_key = bytes.fromhex(key)
# print(key)
# print(pub_key)
