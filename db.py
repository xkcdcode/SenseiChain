import random
from itertools import cycle

from encrypted_search import EncryptedSearch
from iroha_engine import IrohaEngine
from ope import OPEngine
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
import uuid
import datetime
import pprint


class DB:

    def __init__(self):
        # self.db = TinyDB(storage=MemoryStorage)
        self.db = TinyDB('swift.db', sort_keys=False, indent=4, separators=(',', ': '))
        self.table = self.db.table('SWIFT')
        self.engine = OPEngine('secret.key')  # type: OPEngine

    def populate(self, entries):
        chain = IrohaEngine()
        se = EncryptedSearch()
        names_pool = cycle(["Alice", "Bob", "Charlie", "Dave", "Eve"])
        for i in range(entries):
            # print(i)
            value = random.randint(1, 100)  # type: int
            # value = i  # type: int
            tx_id = uuid.uuid4().hex
            date = datetime.datetime.now().timestamp()

            sender_name = next(names_pool)  # type: str
            receiver_name = next(names_pool)  # type: str

            self.table.insert({
                "ref": tx_id,
                "bank_op_code": "CRED",
                "date": date,
                "value": value,
                "currency": "GBP",
                "payers_bank": "BARCGB22XXX",
                "payer": {
                    "IBAN": "GB33BUKB20201555555555",
                    "name": sender_name,
                    "address": "10 Downing Street SW1A 2AA"
                },
                "beneficiary_bank": "HBUKGB4BXXX",
                "beneficiary": {
                    "IBAN": "GB15HBUK40127612345678",
                    "name": receiver_name,
                    "address": "9 Downing Street SW1A 2AA"
                },
                "remittance_info": "",
                "charges": "SHA"
            })

            # Populate the iroha blockchain
            delim = "    "
            tx_data = se.get_name_blind_index(sender_name) + delim + se.encrypt_name(sender_name) + delim + se.get_name_blind_index(receiver_name) \
                      + delim + se.encrypt_name(receiver_name) + delim + str(self.engine.encode(value))
            chain.set_parameters_for_hsbc(tx_id, tx_data)

    def list_all(self):
        # To list all values
        return self.table.all()

    def search_eq_value(self, value):
        # To search and return values
        MT103 = Query()
        val = self.engine.encode(value)
        return self.table.search(MT103.value == val)

    def search_gte_value(self, value):
        # To search and return values
        MT103 = Query()
        val = self.engine.encode(value)
        return self.table.search(MT103.value >= val)

    def search_lt_time(self):
        # To search and return values
        MT103 = Query()
        return self.table.search(MT103.date <= datetime.datetime.now().timestamp())


# For updating the values, use the following commands:
# db.update({'count': 1000}, Magazine.type == 'OSFY')
# res = db.all()
# print(res)

# To remove values, type:
# db.remove(Magazine.count < 900)
# res = db.all()
# print(res)

# To delete all the values, give the following commands:
# db.purge()
# db.all()

if __name__ == "__main__":
    data = DB()
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(type(data.table.all()))
    pp.pprint(data.table.all())
    # print(len(data.list_all()))
    # res = data.search_gte_value(9000000)
    # pp.pprint(res)
    # print(len(res))
    #
    # data.populate_db(5)
    # pp.pprint(data.list_all())
