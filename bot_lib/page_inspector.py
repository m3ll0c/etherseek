import json
import logging
import tldextract

from multiprocessing import Queue

from uuid import uuid4
from pathlib import Path
from playwright.sync_api import sync_playwright


class PageInspector:
    def __init__(self, headless=True):
        self.captures = {}
        self.headless = headless

    def capture_requests(self, urls: list, verbose: bool, settings: dict, queue: Queue, format: str = "dict"):
        """_summary_

        Args:
            urls (list): list of urls to be scanned
            verbose (bool): level of details
            settings (dict): settings of etherseek
            format (str, optional): output format. Defaults to "dict".

        Returns:
            _type_: returns a dictionary with all the captured data
        """
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=Path(f"./{settings["temp_profiles_path"]}/{uuid4()}"),  # creates a unique user data directory
                headless=self.headless,
                args=settings["chromium_flags"]
            )  # headless to add elegance
            page = browser.new_page()
            
            def log_request(request):
                try:

                    url_meta = tldextract.extract(request.url)
                    scanned_url_meta = tldextract.extract(page.url)

                    domain = f"{url_meta.domain}.{url_meta.suffix}"
                    scanned_domain = f"{scanned_url_meta.domain}.{scanned_url_meta.suffix}"

                    if domain not in self.captures:
                        self.captures[domain] = {}

                    if page.url not in self.captures[domain]:
                        self.captures[domain][page.url] = []

                    self.captures[domain][page.url].append({
                        "type": "request",
                        "method": request.method,
                        "scanned_domain": scanned_domain,
                        "domain": domain,
                        "url": request.url,
                        "headers": dict(request.headers),
                        "body": request.post_data
                    })
                    if verbose:
                        logging.info(f"[REQUEST] {request.method} {request.url}")
                except Exception as e:
                    if verbose:
                        logging.error(f"Error when getting request: {e}")

            def log_response(response):
                try:
                    try:
                        body = response.text() # this will fail when open binaries, pay attention to it
                    except:
                        body = "<not available>"

                    url_meta = tldextract.extract(response.url)
                    scanned_url_meta = tldextract.extract(page.url)

                    domain = f"{url_meta.domain}.{url_meta.suffix}"
                    scanned_domain = f"{scanned_url_meta.domain}.{scanned_url_meta.suffix}"

                    self.captures[domain][page.url].append({
                        "type": "response",
                        "status": response.status,
                        "domain": domain,
                        "scanned_domain": scanned_domain,
                        "url": response.url,
                        "headers": dict(response.headers),
                        "body": body,
                        "request_method": response.request.method
                    })
                    if verbose:
                        logging.info(f"[RESPONSE] {response.status} {response.request.method} {response.url}")
                except Exception as e:
                    if verbose:
                        logging.error(f"Error when getting response: {e}")

            # add listener
            page.on("request", log_request)
            page.on("response", log_response)

            for url in urls:
                queue.put(1)
                try:
                    page.goto(url)
                except Exception as e:
                    if verbose:
                        logging.error(f"Error when loading {url}: {e}")
                    pass

            # be civil, close the goddamn browser
            browser.close()
        
        return self.get_results(format)

    def get_results(self, format: str = "dict"):
        """
        Return the captured results.
        @param format: The format to return the results in json|dict.
        """
        if format == "json":
            return json.dumps(self.captures, indent=2, ensure_ascii=False)
        if format == "dict":
            return self.captures
