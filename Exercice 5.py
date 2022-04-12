import requests
import requests_cache
from bs4 import BeautifulSoup

requests_cache.install_cache('demo_cache')


class SiteScraper(object):

    def __init__(self, current_url):
        self.url = current_url
        self.data = []

    def make_request(self):
        return requests.get(self.url).text

    def make_soup(self):
        return BeautifulSoup(self.make_request(), 'html.parser')

    @staticmethod
    def clean(dirty_item):
        return dirty_item.get_text().strip().replace('\n', '')

    def get_data(self):
        for item in self.make_soup().table.find_all('tr'):
            self.data.append(list(map(self.clean, item)))
        return self.data

    def solution(self):
        for counter, item in enumerate(self.get_data()):
            item = [x for x in item if x != '']
            if counter >= 1 and len(item) == 8:
                item.insert(4, '')
            yield item


if __name__ == "__main__":
    get_links = SiteScraper(r'https://www.scrapethissite.com/pages/forms/').solution()
    for i in get_links:
        print(i)

