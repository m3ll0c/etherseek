import json
import pandas as pd

from bot_lib.chain_translator import ChainTranslator


class Transform:
    @classmethod
    def split_list(cls, lst, n_parts):
        """Split list into n_parts (as equal as possible)."""
        k, m = divmod(len(lst), n_parts)
        return [lst[i*k + min(i, m):(i+1)*k + min(i+1, m)] for i in range(n_parts)]

    @classmethod
    def filter_results(cls, results, keyword):
        result = []

        for captures in results:
            for url, data in captures.items():
                if keyword in url:
                    result.append(captures[url])

        return result
    
    @classmethod
    def dataset_maker(cls, filtered_results_: list) -> dict:
        dataset = {
            "scanned_url": [],
            "scanned_domain": [],
            "type": [],
            "domain": [],
            "url": [],
            "contract_address": [],
            "data": [],
            "method": [],
            "result": [],
        }

        for result_process in filtered_results_:
            for url, data in result_process.items():
                for request in data:
                    dataset["scanned_url"].append(url)
                    dataset["scanned_domain"].append(request.get("scanned_domain", ""))
                    dataset["type"].append(request.get("type", ""))
                    dataset["domain"].append(request.get("domain", ""))
                    dataset["url"].append(request.get("url", ""))

                    if request["type"] == "request":
                        body = json.loads(request.get("body", ""))
                        if isinstance(body, dict):
                            if isinstance(body.get("params"), dict):
                                dataset["contract_address"].append(body["params"].get("to", ""))
                                dataset["data"].append(body["params"].get("data", ""))
                                dataset["method"].append(body.get("method", ""))
                            elif isinstance(body.get("params"), list):
                                for param in body["params"]:
                                    if isinstance(param, dict):
                                        dataset["contract_address"].append(param.get("to", ""))
                                        dataset["data"].append(param.get("data", ""))
                                        dataset["method"].append(body.get("method", ""))
                        elif isinstance(body, list):
                            for req in body:
                                if req["method"] == "eth_call":
                                    dataset["contract_address"].append(req.get("to", ""))
                                    dataset["data"].append(req.get("data", ""))
                                    dataset["method"].append(req.get("param", ""))
                    else:
                        dataset["contract_address"].append("")
                        dataset["data"].append("")
                        dataset["method"].append("")

                    if request["type"] == "response":
                        if request.get("body") != "<not available>":
                            body = json.loads(request.get("body", ""))
                            if isinstance(body, dict):
                                dataset["result"].append(body.get("result", ""))
                            elif isinstance(body, list):
                                dataset["result"].append("".join([f"{res.get("result", "")};" for res in body]))
                        else:
                            dataset["result"].append("")
                    else:
                        dataset["result"].append("")
        return dataset
    
    @classmethod
    def compact_and_add_wallet(cls, df: pd.DataFrame, wallets):
        for wallet in wallets:
            df.loc[wallet[0]==df["contract_address"], "wallet"] = wallet[1]

        return df[["scanned_domain", "type", "contract_address", "wallet", "domain"]]