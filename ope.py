from pyope.ope import OPE, ValueRange


class OPEngine:
    def __init__(self, key):
        with open(key) as f:
            secret = f.read()
            f.close()
        self.secret_key = bytes.fromhex(secret)

    def encode(self, value):
        cipher = OPE(self.secret_key, in_range=ValueRange(0, 18446744073709551615),
                     out_range=ValueRange(0, 2173912837129837129832))
        return cipher.encrypt(value)

    def decode(self, value):
        cipher = OPE(self.secret_key, in_range=ValueRange(0, 18446744073709551615),
                     out_range=ValueRange(0, 2173912837129837129832))
        return cipher.decrypt(value)


if __name__ == "__main__":
    eng = OPEngine('secret.key')
    assert eng.encode(1000) < eng.encode(2000) < eng.encode(3000)
    assert eng.decode(eng.encode(1000000000)) == 1000000000
    a = eng.encode(1000)
    b = eng.encode(2000)
    print(a, b)
    c = eng.encode(999)
    print(c)
    print(b-a)
    print(eng.decode(b-a))
    if (b - a) > eng.encode(999):
        print("ALERT")
