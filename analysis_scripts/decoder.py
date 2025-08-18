import re
import gzip
import base64
from web3 import Web3


url_ = "https://data-seed-prebsc-1-s1.binance.org:8545"
url = "https://bsc-dataseed.binance.org/"
contract_address = '0x9179dda8B285040Bf381AABb8a1f4a1b8c37Ed53'

_abi1 = """[
	{
		"inputs": [],
		"name": "get",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "pure",
		"type": "function"
	}
]"""

_abi = """[
  {
    "inputs": [],
    "stateMutability": "nonpayable",
    "type": "constructor"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "string",
        "name": "",
        "type": "string"
      }
    ],
    "name": "E",
    "type": "event"
  },
  {
    "inputs": [
      {
        "internalType": "string",
        "name": "_c",
        "type": "string"
      }
    ],
    "name": "u",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "g",
    "outputs": [
      {
        "internalType": "string",
        "name": "",
        "type": "string"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  }
]"""

w3 = Web3(Web3.HTTPProvider(url))  # Connect to Ethereum node, in this case, binance

contract = w3.eth.contract(address=w3.to_checksum_address(contract_address), abi=_abi)

fn = contract.get_function_by_name("g")()  # optional, needs abi
call_data = fn._encode_transaction_data()  # optional, needs abi

# eth_call, better than requests
raw_result = w3.eth.call({
    "to": contract_address,
    "data": '0x711452e6'  # function used to infect iop.med.br
})

print("Raw result:", raw_result)
print("Decoded result:", bytes.fromhex(raw_result.hex()).decode('utf-8', errors='ignore'))


# Extract the base64-like part
match = re.search(rb'H4sI[0-9A-Za-z+/=]+', raw_result)

if not match:
    raise ValueError("No base64 gzip data found")

b64_data = match.group(0)

# Decompress gzip
decoded_str = gzip.decompress(base64.b64decode(b64_data)).decode('utf-8')  # all this trouble to emulate atob, but it works

print(decoded_str)
