import requests


class APIDiscovery:

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def get(self, endpoint: str, params: dict | None = None):

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        response = requests.get(
            url,
            params=params,
            timeout=60,
            headers={
                "User-Agent": "SikaGle-KnowledgeEngine/1.0"
            }
        )

        response.raise_for_status()

        return response
