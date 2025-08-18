import requests
from web3 import Web3
from eth_abi import encode, decode
import json
import sys

# Configurações
BSC_RPC = "https://bsc-dataseed.binance.org/"
BSCSCAN_API_KEY = "SUA_API_KEY_AQUI"

def get_abi(address):
    url = f"https://api.bscscan.com/api?module=contract&action=getabi&address={address}&apikey={BSCSCAN_API_KEY}"
    resp = requests.get(url).json()
    if resp["status"] != "1":
        raise Exception(f"Erro ao obter ABI: {resp.get('result')}")
    return json.loads(resp["result"])

def find_function_abi(abi, func_name):
    for item in abi:
        if item.get("type") == "function" and item.get("name") == func_name:
            return item
    raise Exception(f"Função {func_name} não encontrada na ABI")

def encode_function_data(function_abi, args):
    # montar assinatura da função ex: balanceOf(address)
    input_types = [inp["type"] for inp in function_abi.get("inputs", [])]
    signature = f"{function_abi['name']}({','.join(input_types)})"

    w3 = Web3()
    function_selector = w3.keccak(text=signature)[:4]  # 4 bytes

    if len(input_types) == 0:
        return function_selector.hex()

    # Codificar argumentos
    encoded_args = encode(input_types, args)
    return (function_selector + encoded_args).hex()

def decode_function_output(function_abi, data):
    output_types = [out["type"] for out in function_abi.get("outputs", [])]
    if len(output_types) == 0:
        return None
    return decode(output_types, data)

def main():
    if len(sys.argv) < 3:
        print("Uso: python script.py <endereco_contrato> <funcao> [arg1 arg2 ...]")
        sys.exit(1)

    contract_address = Web3.to_checksum_address(sys.argv[1])
    function_name = sys.argv[2]
    args = sys.argv[3:]  # argumentos como strings

    # Conexão BSC
    w3 = Web3(Web3.HTTPProvider(BSC_RPC))
    if not w3.is_connected():
        raise Exception("Erro ao conectar à BSC")

    abi = get_abi(contract_address)
    func_abi = find_function_abi(abi, function_name)

    # Converter argumentos para tipos corretos (exemplo simples, pode melhorar)
    input_types = [inp["type"] for inp in func_abi.get("inputs", [])]
    if len(args) != len(input_types):
        raise Exception(f"Número de argumentos incorreto. Esperado {len(input_types)}, recebido {len(args)}")

    # Conversão básica: só para uint, address e bool e string (pode ser extendida)
    def parse_arg(arg, typ):
        if typ.startswith("uint") or typ.startswith("int"):
            return int(arg)
        if typ == "address":
            return Web3.to_checksum_address(arg)
        if typ == "bool":
            return arg.lower() in ("true", "1")
        if typ == "string":
            return arg
        # para arrays e outros tipos complexos, seria necessário parser extra
        return arg

    parsed_args = [parse_arg(a, t) for a, t in zip(args, input_types)]

    data = encode_function_data(func_abi, parsed_args)

    call_params = {
        "to": contract_address,
        "data": data
    }

    raw_result = w3.eth.call(call_params)
    decoded_result = decode_function_output(func_abi, raw_result)

    print(f"Retorno da função {function_name}({', '.join(args)}): {decoded_result}")

if __name__ == "__main__":
    main()
