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

import os
import sys
import json
import shutil
import logging
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


def init_logger(file_path: str, execution_id: str):
    """init logger

    Args:
        file_path (str): file path
        execution_id (str): uuid generate for the directories
    """
    if not os.path.exists(file_path):
        os.mkdir(file_path)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(f"{file_path}/{execution_id}.log", mode="a")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def invoke_inspector(load):
    """utility to run the inspector

    Args:
        load (tuple): 1. urls list, 2. verbose flag, 3. settings dict

    Returns:
        _type_: return capture_requests()
    """
    inspector = PageInspector(headless=True)
    return inspector.capture_requests(load[0], load[1], load[2])


def seek(args: Namespace, settings: dict):
    """Where the real work happens

    Args:
        args (Namespace): Namespace with execution arguments
    """    
    if args.file:
        urls = Retriever.urls_from_local_file(args.file[0], args.file[1])
    elif args.urlscan:
        urls = Retriever.urls_from_urlscan(args.urlscan[0], settings)

    url_parts = Transform.split_list(urls[:10], args.jobs)
    processing_load = [(url_part, args.verbose, settings) for url_part in url_parts]
    
    output_path = f"./{settings["results_path"]}/{args.output}"
    Path(output_path).mkdir(parents=True, exist_ok=True)

    with multiprocessing.Pool(processes=args.jobs) as pool:
        net_packages = pool.map_async(invoke_inspector, processing_load).get()

    filtered_results = Transform.filter_results(net_packages, args.keyword)

    with open(f"{output_path}/results.json", "w+", encoding="utf-8") as f:
        f.write(json.dumps(filtered_results, indent=2))

    dataset = pd.DataFrame(Transform.dataset_maker(filtered_results))
    dataset.to_csv(f"{output_path}/results.csv", index=False)
    print(dataset.head())

    if args.wallets:
        addresses = list(set(dataset["contract_address"].to_list()))

        if not args.chainid:
            chain_name, chain_meta = ChainTranslator.translate(args.keyword)
            wallets = Retriever.wallets(addresses, chain_meta['id'], args.wallets, args.verbose)
        else:
            wallets = Retriever.wallets(addresses, args.chainid, args.wallets, args.verbose)
        
        wallet_dataset = Transform.compact_and_add_wallet(dataset, wallets)
        wallet_dataset.to_csv(f"{output_path}/results_with_wallets-{chain_name.replace(" ",  "-")}.csv")
        print(wallet_dataset.head())

    shutil.rmtree(settings["temp_profiles_path"])
    logging.info(f"Results saved to {output_path}")


if __name__ == "__main__":
    with open("./settings.json") as fp:
        settings = json.load(fp)

    exec_id = str(uuid4())
    init_logger(settings["log_path"], exec_id)

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
    output_group.add_argument('-o', '--output', default=exec_id, help="changes the output path, it uses a random unique identifier as default")
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
        seek(args, settings)
    except Exception as e:
        traceback.print_exc()
