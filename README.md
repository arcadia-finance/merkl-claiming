# merkl-claiming

Start in the python directory:

```bash
cd python
```

Install using:

```bash
poetry shell
poetry install
```

set env variables in .env:

```bash
RPC_URL=https://base.alchemyapi.io/v2/your_alchemy_api_key
TRUSTED_ADDRESS=0xA9DdD91249DFdd450E81E1c56Ab60E1A62651701
TRUSTED_ADDRESS_KEY=some_private_key
```

Run using:

```bash
poetry run python main.py
```