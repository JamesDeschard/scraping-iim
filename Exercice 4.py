import requests
import requests_cache
from bs4 import BeautifulSoup

requests_cache.install_cache('demo_cache')


class SiteScraper(object):

    def __init__(self, current_url):
        self.url = current_url
        self.data = {}

    def make_request(self):
        return requests.get(self.url).text

    def make_soup(self):
        return BeautifulSoup(self.make_request(), 'html.parser')

    def get_links(self):
        soup = self.make_soup()
        return soup.find_all(class_='ct-slideshow__slide__text-container')

    def get_data(self):
        raw_data = self.get_links()

        for item in raw_data:
            title = self.clean_string(item.h2)
            paragraphs = item.find_all('p')
            meta = self.clean_string(paragraphs[0])
            description = self.clean_string(paragraphs[1])
            self.data[title] = [meta, description]

        return self.data

    @staticmethod
    def clean_string(dirty_string):
        return dirty_string.get_text().replace('\n', '')


if __name__ == "__main__":
    get_links = SiteScraper(r'https://stacker.com/stories/1587/100-best-movies-all-time').get_data()
    for key, value in get_links.items():
        print(key, value)
