import json
import time
import requests
import pandas as pd
import traceback

class Retriever:
    @classmethod
    def urls_from_urlscan(cls, api_key: str, settings: dict) -> list:
        """retrieve urls from urlscan search api

        Args:
            api_key (str): for this specific query you will need an urlscan pro account
            settings (dict): dict with etherseek configuration

        Returns:
            list : list with unique urls
        """
        response = requests.get(
            "https://urlscan.io/api/v1/search/", 
            headers={
            "Content-Type": "application/json", "API-Key": api_key
            }, 
            params={
            "q": settings["urlscan_query"],
            "size": 10000
            }
        )

        if response.status_code == 200:
            data = json.loads(response.text)
            urls = list(set([result['task']['url'] for result in data['results']]))
        
        return urls

    @classmethod
    def urls_from_local_file(cls, path: str, column: str) -> list:
        """loads into memory urls from a csv file

        Args:
            path (str): path to the csv file
            column (str): column to extract data

        Returns:
            list: list with unique urls
        """
        df = pd.read_csv(path, encoding="utf-8")
        return list(set(df[column].tolist()))
    
    @classmethod
    def wallets(cls, smart_contracts: list, chain_id: int, api_token: str, verbose: bool) -> list:
        """_summary_

        Args:
            smart_contracts (list): list with smart contracts addresses
            chain_id (int): chain id integer, can be found on etherscan documentation, automated using ChainTranslator Class
            api_token (str): you can get it by creating an account on etherscan

        Returns:
            list: returns a list with tuples (contract, wallet)
        """
        results = []

        for contract in smart_contracts:
            try:
                if isinstance(contract, str):
                    response = requests.post(
                        f"https://api.etherscan.io/v2/api?chainid={chain_id}&module=contract&action=getcontractcreation&contractaddresses={contract}&apikey={api_token}",
                    )

                    if contract != '' and response.status_code == 200:
                        response_data = json.loads(response.text)
                        results.append((contract, response_data["result"][0]["contractCreator"]))

                    time.sleep(0.2)  # etherscan only allow 5 queries per second in the free tier

            except Exception as e:
                if verbose:
                    traceback.print_exc()
        
        return results