import requests
import xml.etree.ElementTree as ET


class SitemapDiscovery:

    def __init__(self, sitemap_url: str):

        self.sitemap_url = sitemap_url

    def discover(self):

        response = requests.get(
            self.sitemap_url,
            timeout=60,
            headers={
                "User-Agent": "SikaGle-KnowledgeEngine/1.0"
            }
        )

        response.raise_for_status()

        root = ET.fromstring(
            response.content
        )

        urls = []

        for element in root.iter():

            if element.tag.endswith("loc"):

                if element.text:

                    urls.append(
                        element.text.strip()
                    )

        return urls
