import json
import shutil
import multiprocessing
import pandas as pd

from uuid import uuid4 
from pathlib import Path

from lib.page_inspector import PageInspector
from lib.filter_interface import FilterInterface  


def invoke_inspector(load):
    inspector = PageInspector(headless=True)
    return inspector.capture_requests(load)


def filter_results(results, keyword):
    result = []

    for captures in results:
        for url, data in captures.items():
            if keyword in url:
                result.append(captures[url])

    return result

def split_list(lst, n_parts):
    """Split list into n_parts (as equal as possible)."""
    k, m = divmod(len(lst), n_parts)
    return [lst[i*k + min(i, m):(i+1)*k + min(i+1, m)] for i in range(n_parts)]


def dataset_maker(filtered_results_: list):
    dataset = {
        "scanned_url": [],
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
    return dataset
                

if __name__ == "__main__":
    urls = [
        "http://iop.med.br/exames-3",
        "https://ceopucv.cl/wp/",
        "https://casef.cl/",
        "https://vivversaudepublica.com.br/tag/sistema-de-gestao/",
        "https://www.maissauderevista.com.br/",
        "https://celvmarilia.org.br/"
        ]
    
    url_parts = split_list(urls, 3)  # split the list into 3 parts for multiprocessing
    
    output_path = f"./results/{uuid4()}/"

    with multiprocessing.Pool(processes=3) as pool:
        net_packages = pool.map_async(invoke_inspector, url_parts).get()

    filtered_results = filter_results(net_packages, "binance.")  # more elegant solution in the works

    Path(output_path).mkdir(parents=True, exist_ok=True)  # ensure the directory exists

    with open(f"{output_path}/results.json", "w+", encoding="utf-8") as f:
        f.write(json.dumps(filtered_results, indent=2))

    df = pd.DataFrame(dataset_maker(filtered_results))

    print(df.head())  # print the first few rows of the DataFrame

    df.to_csv(f"{output_path}/results.csv", index=False)  # save DataFrame to CSV

    shutil.rmtree("./mock_data/")  # clean up the output directory after use
    print(f"Results saved to {output_path}/results.json")
