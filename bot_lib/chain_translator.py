from bot_lib.values import CHAINS

class ChainTranslator:

    @classmethod
    def translate(cls, domain: str) -> object:
        """Finds a desired network, with domain, the whole dictionary can be found on values.py

        Args:
            domain (str): domain name

        Returns:
            object: return a tuple with key, value of the matched network
        """
        for chain, meta in CHAINS.items():
            for endpoint in meta["domain_endpoints"]:
                if domain in endpoint:
                    return (chain, meta)
        return None