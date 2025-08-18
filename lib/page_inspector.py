import json
import tldextract
from uuid import uuid4
from pathlib import Path
from playwright.sync_api import sync_playwright


class PageInspector:
    def __init__(self, headless=True):
        self.captures = {}
        self.headless = headless

    def capture_requests(self, urls: list, format: str = "dict"):
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=Path(f"./mock_data/{uuid4()}"),  # creates a unique user data directory
                headless=self.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-client-side-phishing-detection",
                    "--safebrowsing-disable-download-protection",
                    "--safebrowsing-disable-auto-update",
                    "--disable-popup-blocking"
                ]
            )  # headless to add elegance
            page = browser.new_page()
            
            def log_request(request):
                try:

                    url_meta = tldextract.extract(request.url)

                    domain = f"{url_meta.domain}.{url_meta.suffix}"
                    if domain not in self.captures:
                        self.captures[domain] = {}

                    if page.url not in self.captures[domain]:
                        self.captures[domain][page.url] = []

                    self.captures[domain][page.url].append({
                        "type": "request",
                        "method": request.method,
                        "url": request.url,
                        "headers": dict(request.headers),
                        "body": request.post_data
                    })

                    print(f"[REQUEST] {request.method} {request.url}")
                except Exception as e:
                    print(f"Error when getting request: {e}")

            def log_response(response):
                try:
                    try:
                        body = response.text() # this will fail when open binaries, pay attention to it
                    except:
                        body = "<not available>"

                    url_meta = tldextract.extract(response.url)
                    
                    domain = f"{url_meta.domain}.{url_meta.suffix}"

                    self.captures[domain][page.url].append({
                        "type": "response",
                        "status": response.status,
                        "url": response.url,
                        "headers": dict(response.headers),
                        "body": body,
                        "request_method": response.request.method
                    })

                    print(f"[RESPONSE] {response.status} {response.request.method} {response.url}")
                except Exception as e:
                    print(f"Error when getting response: {e}")

            # add listener
            page.on("request", log_request)
            page.on("response", log_response)

            for url in urls:
                page.goto(url)

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
