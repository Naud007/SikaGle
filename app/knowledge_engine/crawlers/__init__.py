from .base_crawler import BaseCrawler
from .inrab_crawler import INRABCrawler

__all__ = [
    "BaseCrawler",
    "INRABCrawler",
]
def __init__(self):
    super().__init__()

    self.parser = INRABPublicationParser()
