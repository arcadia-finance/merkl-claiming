from web3 import Web3
import json
import os
import dotenv
from multicall import Multicall, Call
import asyncio

dotenv.load_dotenv(dotenv_path='.env')
RPC_URL = os.getenv('RPC_URL')

w3 = Web3(Web3.HTTPProvider(RPC_URL))

with open('jsons/distributor_abi.json') as f:
    distributor_abi = json.load(f)

with open('jsons/arcadia_factory_abi.json') as f:
    arcadia_factory_abi = json.load(f)

distributor = w3.eth.contract(address='0x3Ef3D8bA38EBe18DB133cEc108f4D14CE00Dd9Ae', abi=distributor_abi)
arcadia_factory = w3.eth.contract(address='0xDa14Fdd72345c4d2511357214c5B89A919768e59', abi=arcadia_factory_abi)
CLAIMER = "0x3146e7bCeE81aE5a9BDcC8452ba7bBf9f8524205"

async def get_accounts(amount_of_accounts):
    def from_value(value):
        return Web3.to_checksum_address(value) 
    
    accounts = []
    index_arr = list(range(amount_of_accounts))
    for i in range(0, amount_of_accounts, 100):
        batch = index_arr[i:i+100]
        calls = [
            Call("0xDa14Fdd72345c4d2511357214c5B89A919768e59", ["allAccounts(uint256)(address)", index], [(str(index), from_value)]) for index in batch
        ]
        multicall = Multicall(calls, _w3=w3)
        results = await multicall.coroutine()
        accounts.extend([results[str(x)] for x in batch])
    return accounts

async def get_operator_status(accounts):
    is_operator_set = {}
    for i in range(0, len(accounts), 100):
        batch = accounts[i:i+100]
        calls = [
            Call("0x3Ef3D8bA38EBe18DB133cEc108f4D14CE00Dd9Ae", ["operators(address,address)(bool)", account, CLAIMER], [(account, None)]) for account in batch
        ]
        multicall = Multicall(calls, _w3=w3)
        results = await multicall.coroutine()
        is_operator_set.update({account: True if results[account] == 1 else False for account in batch})

    return is_operator_set


async def get_accounts_without_operator():
    amount_of_accounts = arcadia_factory.functions.allAccountsLength().call()
    all_accounts = await get_accounts(amount_of_accounts)

    is_operator_set = await get_operator_status(all_accounts)
    accounts_to_set_operator = [account for account, value in is_operator_set.items() if value is False]    

    with open('accounts_unset_operators.json', '+w') as f:
        f.write(json.dumps(accounts_to_set_operator))

    return accounts_to_set_operator

if __name__ == "__main__":
    asyncio.run(get_accounts_without_operator())