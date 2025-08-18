import json
import multiprocessing
from lib.page_inspector import PageInspector
from lib.filter_interface import FilterInterface  


def invoke_inspector(urls):
    inspector = PageInspector(headless=False)
    return inspector.capture_requests(urls)


def filter_results(results, keyword):
    return results


if __name__ == "__main__":
    urls = [
        "http://iop.med.br/exames-3",
        "https://ceopucv.cl/wp/"
        ]
    
    saida_arquivo = "packages_out.json"

    net_packages = []

    url_parts = [[urls[0]], [urls[1]]]

    with multiprocessing.Pool(processes=3) as pool:
        net_packages.append(pool.map_async(invoke_inspector, url_parts).get())

    filtered_results = filter_results(net_packages, "binance")  # more elegant solution in the works

    with open(saida_arquivo, "w", encoding="utf-8") as f:
        f.write(json.dumps(filtered_results, indent=2)) 
