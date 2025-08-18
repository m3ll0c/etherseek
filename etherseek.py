import json
import shutil
import multiprocessing
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

    shutil.rmtree("./mock_data/")  # clean up the output directory after use
    print(f"Results saved to {output_path}/results.json")
