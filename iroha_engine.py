import datetime
import json
import os
import binascii
import pprint
import random
import uuid
from ast import literal_eval
from itertools import cycle

from iroha import IrohaCrypto
from iroha import Iroha, IrohaGrpc
from iroha.primitive_pb2 import can_set_my_account_detail

from encrypted_search import EncryptedSearch
from ope import OPEngine


class IrohaEngine:
    IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', '127.0.0.1')
    IROHA_PORT = os.getenv('IROHA_PORT', '50051')
    ADMIN_ACCOUNT_ID = os.getenv('ADMIN_ACCOUNT_ID', 'admin@test')
    ADMIN_PRIVATE_KEY = os.getenv('ADMIN_PRIVATE_KEY', 'f101537e319568c765b2cc89698325604991dca57b9716b58016b253506cab70')

    def __init__(self):

        self.engine = OPEngine('secret.key')  # type: OPEngine
        self.se = EncryptedSearch()  # type: EncryptedSearch
        self.delim = "    "  # type: str

        with open('hsbc.pub') as f:
            pub_key = f.read()
            f.close()

        with open('hsbc.pri') as f:
            pri_key = f.read()
            f.close()

        self.hsbc_pub_key = bytes.fromhex(pub_key)
        self.hsbc_pri_key = bytes.fromhex(pri_key)

        self.m_domain = 'swift'
        self.m_asset = 'mt103'
        self.m_account = 'hsbc'

        self.iroha = Iroha(self.ADMIN_ACCOUNT_ID)
        self.net = IrohaGrpc('{}:{}'.format(self.IROHA_HOST_ADDR, self.IROHA_PORT))

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
    def send_transaction_and_print_status(self, transaction):
        hex_hash = binascii.hexlify(IrohaCrypto.hash(transaction))
        print(f'Transaction hash = {hex_hash}, creator = {transaction.payload.reduced_payload.creator_account_id}')
        self.net.send_tx(transaction)
        for status in self.net.tx_status_stream(transaction):
            print(status)

    @trace
    def create_domain_and_asset(self):
        """
        Creates domain 'SWIFT' and asset 'mt103#SWIFT' with precision 0
        """
        commands = [
            self.iroha.command('CreateDomain', domain_id=self.m_domain, default_role='user'),
            self.iroha.command('CreateAsset', asset_name=self.m_asset, domain_id=self.m_domain, precision=0)
        ]
        tx = IrohaCrypto.sign_transaction(self.iroha.transaction(commands), self.ADMIN_PRIVATE_KEY)
        self.send_transaction_and_print_status(tx)

    @trace
    def create_account_hsbc(self):
        """
        Create account 'HSBC@SWIFT'
        """
        tx = self.iroha.transaction([
            self.iroha.command('CreateAccount', account_name=self.m_account, domain_id=self.m_domain, public_key=self.hsbc_pub_key)
        ])
        IrohaCrypto.sign_transaction(tx, self.ADMIN_PRIVATE_KEY)
        self.send_transaction_and_print_status(tx)

    @trace
    def hsbc_grants_to_admin_set_account_detail_permission(self):
        """
        Make admin@test able to set detail to HSBC@SWIFT
        """
        tx = self.iroha.transaction([
            self.iroha.command('GrantPermission', account_id='admin@test', permission=can_set_my_account_detail)
        ], creator_account=self.m_account + "@" + self.m_domain)
        IrohaCrypto.sign_transaction(tx, self.hsbc_pri_key)
        self.send_transaction_and_print_status(tx)

    @trace
    def set_parameters_for_hsbc(self, ref, mt103):
        """
        Set parameters to hsbc@swift by admin@test
        """
        tx = self.iroha.transaction(
            [self.iroha.command('SetAccountDetail', account_id=self.m_account + "@" + self.m_domain, key=ref, value=mt103)])
        IrohaCrypto.sign_transaction(tx, self.ADMIN_PRIVATE_KEY)
        self.send_transaction_and_print_status(tx)

    @trace
    def get_hsbc_details(self):
        """
        Get all the kv-storage entries for HSBC@SWIFT
        """
        query = self.iroha.query('GetAccountDetail', account_id=self.m_account + '@' + self.m_domain)
        IrohaCrypto.sign_query(query, self.ADMIN_PRIVATE_KEY)

        response = self.net.send_query(query)
        data = response.account_detail_response
        print(f'Account id = {self.m_account + "@" + self.m_domain} : Details :-')

        result = data.detail  # type: str
        print(type(result))
        if not result or result == "{}":
            print("Result is Empty")
        else:
            print(data.detail)
            test = json.loads(result)
            pprint.pprint(test['admin@test'])

    def list_all(self):
        # To list all transactions
        query = self.iroha.query('GetAccountDetail', account_id=self.m_account + '@' + self.m_domain)
        IrohaCrypto.sign_query(query, self.ADMIN_PRIVATE_KEY)

        response = self.net.send_query(query)
        data = response.account_detail_response
        result = data.detail
        if not result or result == "{}":
            print("Result is Empty")
            return None
        else:
            whole_dict = literal_eval(data.detail)  # type: dict
            result_dict = whole_dict["admin@test"]  # type: dict
            return result_dict

    # Iroha is normally populated by the DB class in db.py
    def populate_iroha(self, entries):
        names_pool = cycle(["Alice", "Bob", "Charlie", "Dave", "Eve"])
        for i in range(entries):
            value = random.randint(1, 100)  # type: int
            tx_id = uuid.uuid4().hex
            sender_name = next(names_pool)  # type: str
            receiver_name = next(names_pool)  # type: str

            tx_data = self.se.get_name_blind_index(sender_name) + self.delim + self.se.encrypt_name(sender_name) + self.delim \
                      + self.se.get_name_blind_index(receiver_name) + self.delim + self.se.encrypt_name(receiver_name) + self.delim \
                      + str(self.engine.encode(value))
            print(tx_data)
            self.set_parameters_for_hsbc(tx_id, tx_data)

    def search_value(self, op, value):
        # To search and return transactions
        enc_val = self.engine.encode(value)
        transactions = list()

        query = self.iroha.query('GetAccountDetail', account_id=self.m_account + '@' + self.m_domain)
        IrohaCrypto.sign_query(query, self.ADMIN_PRIVATE_KEY)

        response = self.net.send_query(query)
        data = response.account_detail_response
        result = data.detail  # type: str
        if not result or result == "{}":
            print("Result is Empty")
            return list()
        else:
            whole_dict = literal_eval(data.detail)  # type: dict
            result_dict = whole_dict["admin@test"]  # type: dict

            for tx_id, tx_data in result_dict.items():
                tx_datum = tx_data.split(self.delim)
                tx_datum_val = int(tx_datum[-1])
                if op == "eq":
                    if tx_datum_val == enc_val:
                        # print(tx_id)
                        transactions.append(tx_id + self.delim + tx_data)

                if op == "lte":
                    if tx_datum_val <= enc_val:
                        # print(tx_id)
                        transactions.append(tx_id + self.delim + tx_data)

                if op == "gte":
                    if tx_datum_val >= enc_val:
                        # print(tx_id)
                        transactions.append(tx_id + self.delim + tx_data)

            if not transactions:
                return list()
            else:
                return transactions

    def search_name(self, name):
        # To search and return transactions
        if not name:
            return list()
        blind_index = self.se.find_name(name)
        transactions = list()

        query = self.iroha.query('GetAccountDetail', account_id=self.m_account + '@' + self.m_domain)
        IrohaCrypto.sign_query(query, self.ADMIN_PRIVATE_KEY)

        response = self.net.send_query(query)
        data = response.account_detail_response
        result = data.detail  # type: str
        if not result or result == "{}":
            print("Result is Empty")
            return list()
        else:
            whole_dict = literal_eval(data.detail)  # type: dict
            result_dict = whole_dict["admin@test"]  # type: dict

            for tx_id, tx_data in result_dict.items():
                tx_datum = tx_data.split(self.delim)  # type: list
                if blind_index == tx_datum[0] or blind_index == tx_datum[2]:
                    transactions.append(tx_id + self.delim + tx_data)

            if not transactions:
                return list()
            else:
                return transactions


if __name__ == "__main__":
    ir = IrohaEngine()
    pp = pprint.PrettyPrinter(indent=4)

    # Run the following three functions only at the initialisation time. Maybe put them in the
    # constructor later on

    # ir.create_domain_and_asset()
    # ir.create_account_hsbc()
    # ir.hsbc_grants_to_admin_set_account_detail_permission()

    # ir.populate_iroha(5)

    # ir.get_hsbc_details()
    # my_dict = ir.list_all()     # type: dict
    # pp.pprint(my_dict)

    # results = ir.search_value("eq", 9)
    # pp.pprint(results)
