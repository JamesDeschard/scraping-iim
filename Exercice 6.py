import requests
import requests_cache
from bs4 import BeautifulSoup
import string

requests_cache.install_cache('demo_cache')


class SiteScraper(object):

    def __init__(self, current_url):
        self.url = current_url
        self.base_url = "https://www.flutetunes.com/"
        self.urls = []
        self.score_data = {}

    @staticmethod
    def make_request(url):
        return requests.get(url).text

    def make_soup(self, url):
        return BeautifulSoup(self.make_request(url), 'html.parser')

    def get_urls(self):
        table = self.make_soup(self.url).find('table', {'class': 'tunes'})
        for row in table.find_all('tr')[1:]:
            self.urls.append(row.a['href'])
        return self.urls

    def get_data_from_urls(self, limit):
        self.get_urls()
        for url in self.urls[:limit]:
            soup = self.make_soup(f'{self.base_url}{url}')
            main_title = soup.find(id='content').h2.get_text()
            self.score_data[main_title] = []
            for entry in soup.table.find_all('tr'):
                title = entry.th
                description = entry.td
                if title is not None:
                    description = f'{self.base_url}{description.a["href"]}' \
                        if description.a and title.get_text() != 'Categories' else description.get_text()
                    self.score_data[main_title].append([title.get_text(), description])
        return self.score_data


if __name__ == "__main__":
    alphabet = string.ascii_uppercase
    all_scores = {}

    for letter in alphabet[:1]:
        all_scores[f'starts_with_{letter}'] = SiteScraper(
            f'https://www.flutetunes.com/titles.php?a={letter}'
        ).get_data_from_urls(1)

    print(all_scores)