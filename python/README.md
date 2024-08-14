Install using:

```bash
poetry shell
poetry install
```

set env variables in .env:

```bash
RPC_URL=https://eth-mainnet.alchemyapi.io/v2/your_alchemy_api_key
TRUSTED_ADDRESS=0xA9DdD91249DFdd450E81E1c56Ab60E1A62651701
TRUSTED_ADDRESS_KEY=your_private_key
```

Run using:

```bash
poetry run python main.py
```