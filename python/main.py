from get_unset_accounts import get_accounts_without_operator
from web3 import Web3
import json
import os
import dotenv
import asyncio

dotenv.load_dotenv(dotenv_path='.env')
RPC_URL = os.getenv('RPC_URL')

w3 = Web3(Web3.HTTPProvider(RPC_URL))

with open('jsons/distributor_abi.json') as f:
    distributor_abi = json.load(f)

distributor = w3.eth.contract(address='0x3Ef3D8bA38EBe18DB133cEc108f4D14CE00Dd9Ae', abi=distributor_abi)
CLAIMER = "0x3146e7bCeE81aE5a9BDcC8452ba7bBf9f8524205"
TRUSTED_ADDRESS = os.getenv('TRUSTED_ADDRESS')
TRUSTED_ADDRESS_KEY = os.getenv('TRUSTED_ADDRESS_KEY')

async def send_txes():
    accounts_to_process = await get_accounts_without_operator()

    print(f"Setting operator for {len(accounts_to_process)} accounts")

    nonce = w3.eth.get_transaction_count(TRUSTED_ADDRESS)
    for i in range(0, len(accounts_to_process), 20):
        batch = accounts_to_process[i:i+20]
        batch_txes = []
        gas_price = w3.eth.gas_price
        
        for account in batch:
            tx = distributor.functions.toggleOperator(account, CLAIMER).build_transaction({
                'from': TRUSTED_ADDRESS,
                "maxFeePerGas": gas_price,
                "nonce": nonce,
                "chainId": 8453
            })
            nonce += 1
            tx_signed = w3.eth.account.sign_transaction(tx, TRUSTED_ADDRESS)
            tx_hash = w3.eth.send_raw_transaction(tx_signed.rawTransaction)
            print(tx_hash.hex())
            batch_txes.append(tx_hash.hex())
        
        for tx_hash in batch_txes:
            w3.eth.wait_for_transaction_receipt(tx_hash)
        

if __name__ == "__main__":
    asyncio.run(send_txes())