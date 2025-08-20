# .·:'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''':·.
# : :  ███████████████  █████                       █████████               █████      : :
# : : ░░███░░░░░░░███  ░░███                       ███░░░░░███             ░░███       : :
# : :  ░███  █ ░███████ ░███████   ██████ ████████░███    ░░░  ██████ ██████░███ █████ : :
# : :  ░██████ ░░░███░  ░███░░███ ███░░██░░███░░██░░█████████ ███░░█████░░██░███░░███  : :
# : :  ░███░░█   ░███   ░███ ░███░███████ ░███ ░░░ ░░░░░░░░██░██████░███████░██████░   : :
# : :  ░███ ░   █░███ ██░███ ░███░███░░░  ░███     ███    ░██░███░░░░███░░░ ░███░░███  : :
# : :  ██████████░░█████████ ████░░██████ █████   ░░█████████░░█████░░██████████ █████ : :
# : : ░░░░░░░░░░  ░░░░░░░░░ ░░░░░ ░░░░░░ ░░░░░     ░░░░░░░░░  ░░░░░░ ░░░░░░░░░░ ░░░░░  : :
# '·:..................................................................................:·'

import json
import shutil
import argparse
import traceback
import multiprocessing
import pandas as pd

from uuid import uuid4 
from pathlib import Path
from argparse import Namespace

from bot_lib.values import CHAINS, INTRO
from bot_lib.page_inspector import PageInspector
from bot_lib.chain_translator import ChainTranslator
from bot_lib.transform import Transform
from bot_lib.retriever import Retriever


def invoke_inspector(load):
    inspector = PageInspector(headless=True)
    return inspector.capture_requests(load[0], load[1])


def seek(args: Namespace):
    """Where the real work happens

    Args:
        args (Namespace): Namespace with execution arguments
    """
    print(args)
    
    if "file" in args:
        urls = Retriever.urls_from_local_file(args.file[0], args.file[1])
    elif "urlscan" in args:
        urls = Retriever.urls_from_urlscan(args.urlscan[0])

    url_parts = Transform.split_list(urls[:10], args.jobs)
    processing_load = [(url_part, args.verbose) for url_part in url_parts]
    
    output_path = f"./results/{args.output}"
    Path(output_path).mkdir(parents=True, exist_ok=True)

    with multiprocessing.Pool(processes=args.jobs) as pool:
        net_packages = pool.map_async(invoke_inspector, processing_load).get()

    filtered_results = Transform.filter_results(net_packages, args.keyword)

    with open(f"{output_path}/results.json", "w+", encoding="utf-8") as f:
        f.write(json.dumps(filtered_results, indent=2))

    dataset = pd.DataFrame(Transform.dataset_maker(filtered_results))
    dataset.to_csv(f"{output_path}/results.csv", index=False)

    if args.wallets:
        addresses = list(set(dataset["contract_address"].to_list()))

        if not args.chainid:
            chain_name, chain_meta = ChainTranslator.translate(args.keyword)
            wallets = Retriever.wallets(addresses, chain_meta['id'], args.wallets)
        else:
            wallets = Retriever.wallets(addresses, args.chainid, args.wallets)
        
        wallet_dataset = Transform.compact_and_add_wallet(dataset, wallets)
        wallet_dataset.to_csv(f"{output_path}/results_with_wallets-{chain_name.replace(" ",  "-")}.csv")
        print(wallet_dataset.head())

    shutil.rmtree("./mock_data/")
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    print(INTRO)
    parser = argparse.ArgumentParser()

    data_source = parser.add_mutually_exclusive_group(required=True)
    data_source.add_argument(
                            '-f', '--file', action="store", nargs=2,
                            help="specify the filepath, should be a csv file, if used, column name is REQUIRED",
                            metavar=("file","column_name") 
                            )
    data_source.add_argument('-u', '--urlscan', action="store", nargs=1,
                             help="uses urlscan as a source for compromised urls (you can change the query with the config file), it needs an API KEY",
                             metavar=("api_key") 
                             )

    output_group = parser.add_argument_group('output')
    output_group.add_argument('-o', '--output', default=str(uuid4()), help="changes the output path, it uses a random unique identifier as default")
    output_group.add_argument('-r', '--raw', default=False, action="store_true", help="saves the raw network data, it is a little storage expensive")

    analysis_group = parser.add_argument_group('analysis')
    analysis_group.add_argument('-k', '--keyword', default=None, required=True, help="specify the keyword for the request url, 'binance' is fully supported")
    analysis_group.add_argument('-w', '--wallets', default=None, help="retrieves wallets from etherscan, an api key is REQUIRED, wallet analysis bypass if not specified")
    analysis_group.add_argument('-ci', '--chainid', default=None,  type=int, help="specify the chain id to verify the wallets, it defaults to a guess based on the request domain")

    process_group = parser.add_argument_group('process')
    process_group.add_argument('-j', '--jobs', default=1,  type=int, help="specify the number of parallel processes, it is async for performance sake")
    process_group.add_argument('-v', '--verbose', default=False, action="store_true", help="give the gruesome details, i sugest to leave it on, but the default is false")

    args = parser.parse_args()

    try:
        seek(args)
    except Exception as e:
        if args.verbose:
            traceback.print_exc()
        else:
            print(e)
