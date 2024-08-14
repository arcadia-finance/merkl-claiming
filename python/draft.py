from web3 import Web3
import json
import requests
import os
import dotenv

dotenv.load_dotenv(dotenv_path='.env')
RPC_URL = os.getenv('RPC_URL')

w3 = Web3(Web3.HTTPProvider(RPC_URL))

with open('distributor_abi.json') as f:
    distributor_abi = json.load(f)

with open('accounts.json') as f:
    accounts = json.load(f)

with open('arcadia_factory_abi.json') as f:
    arcadia_factory_abi = json.load(f)

distributor = w3.eth.contract(address='0x3Ef3D8bA38EBe18DB133cEc108f4D14CE00Dd9Ae', abi=distributor_abi)
arcadia_factory = w3.eth.contract(address='0xDa14Fdd72345c4d2511357214c5B89A919768e59', abi=arcadia_factory_abi)
CLAIMER = "0x3146e7bCeE81aE5a9BDcC8452ba7bBf9f8524205"

is_operator_set = {}
amount_of_accounts = arcadia_factory.functions.allAccountsLength().call()
for i in range(0, amount_of_accounts):
    account_address = arcadia_factory.functions.allAccounts(i).call()
    is_operator = distributor.functions.operators(account_address, CLAIMER).call()
    if is_operator == 1:
        is_operator_set[account_address] = True
    else:
        is_operator_set[account_address] = False

accounts_to_set_operator = [key for key, value in is_operator_set.items() if value is False]

claims = {}
for i, account in enumerate(accounts):
    if account["address"] in claims.keys():
        continue
    r = requests.get(f'https://api.merkl.xyz/v3/userRewards?user={account["address"]}&chainId=8453&proof=true')
    resp = r.json()
    resp["operator_set"] = is_operator_set.get(account["address"], False)
    claims.update({account["address"]: resp})
    print(i, len(accounts))

claim_amounts = {}
for claim_address in claims.keys():
    if claims.get('operator_set', False) is False:
        continue
    for asset_to_claim in claims[claim_address]:
        if asset_to_claim == 'operator_set':
            continue
        if claim_amounts.get(asset_to_claim, None) is None:
            claim_amounts[asset_to_claim] = float(claims[claim_address][asset_to_claim]['unclaimed'])
        else:
            claim_amounts[asset_to_claim] += float(claims[claim_address][asset_to_claim]['unclaimed'])

print(claim_amounts)

claim_users = []
claim_tokens = []
claim_amounts = []
claim_proofs = []
usd_total = 0
for claim_address in claims.keys():
    for asset_to_claim in claims[claim_address].keys():
        if asset_to_claim == 'operator_set':
            continue
        usd_value = 0
        unclaimed_amount  = int(claims[claim_address][asset_to_claim]['unclaimed'])
        if unclaimed_amount > 0:
            if asset_to_claim == "0xc3De830EA07524a0761646a6a4e4be0e114a3C83" and unclaimed_amount < 10**17:
                continue
            if asset_to_claim == "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913" and unclaimed_amount < 10**6:
                continue
            if asset_to_claim == '0xc1CBa3fCea344f92D9239c08C0568f6F2F0ee452' and unclaimed_amount < (10**18/3500):
                continue
            if asset_to_claim == "0xc3De830EA07524a0761646a6a4e4be0e114a3C83":
                usd_value = unclaimed_amount * 9.5 / 10**18
            if asset_to_claim == "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913":
                usd_value = unclaimed_amount /10**6
            if asset_to_claim == '0xc1CBa3fCea344f92D9239c08C0568f6F2F0ee452':
                usd_value = unclaimed_amount * 4500 / 10**18
            usd_total += usd_value
            claim_users.append(claim_address)
            claim_tokens.append(asset_to_claim)
            claim_amounts.append(int(claims[claim_address][asset_to_claim]['unclaimed']))
            claim_proofs.append(claims[claim_address][asset_to_claim]['proof'])

# w3 = Web3(Web3.HTTPProvider("https://virtual.base.rpc.tenderly.co/398e8168-15b0-4df8-bb1e-04a5d238b23e"))
# distributor = w3.eth.contract(address='0x3Ef3D8bA38EBe18DB133cEc108f4D14CE00Dd9Ae', abi=distributor_abi)

# for i in range(0, len(claim_users), 200):
#     end_index = min(i + 50, len(claim_users))
#     tx = distributor.functions.claim(claim_users[i:end_index], claim_tokens[i:end_index], claim_amounts[i:end_index], claim_proofs[i:end_index]).build_transaction({
#         'from': '0x3146e7bCeE81aE5a9BDcC8452ba7bBf9f8524205',
#         'gasPrice': w3.to_wei('1', 'gwei')
#     })
#     print(tx)
#     tx_hash = w3.eth.send_transaction(tx)

#     w3.eth.estimate_gas(tx)
#     break