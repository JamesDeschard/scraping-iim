import copy
import itertools
import logging
import time

import requests
import requests_cache
from bs4 import BeautifulSoup, NavigableString

logging.basicConfig(level=logging.INFO)
requests_cache.install_cache('demo_cache')


class GetSoup(object):
    def __init__(self, relevant_url):
        self.url = relevant_url
        self.soup = self.get_soup()

    def get_request(self):
        return requests.get(self.url).text

    def get_soup(self):
        return BeautifulSoup(self.get_request(), 'html.parser')


class PrettyDataMixin(object):
    @staticmethod
    def organize_nameless_headers(counter, html_string, header_length):
        replacement = html_string
        if counter == 1:
            replacement = "Détails du Joueur"
        elif counter == len(header_length):
            replacement = "Matchs"
        return replacement

    @staticmethod
    def clean(html_string_representation) -> str:
        return html_string_representation.get_text()


class TableScraper(GetSoup, PrettyDataMixin):
    def __init__(self, base_url, url, table):
        GetSoup.__init__(self, url)
        self.base_url = base_url
        self.table = table
        self.double_header = False
        self.headers = {}
        self.data = []

    def get_table(self) -> BeautifulSoup:
        return self.soup.find(id=self.table)

    def get_table_title(self) -> str:
        return self.clean(self.get_table().h2)

    def get_table_headers(self) -> dict:
        header = self.get_table().find('thead')
        header = list(filter(lambda obj: type(obj) != NavigableString, header.find_all('tr')))

        if len(header) == 2:
            self.double_header = True
            start = 0
            first_header = header[0].find_all('th')
            second_headers = header[1].find_all('th')
            for counter, item in enumerate(first_header, 1):
                replacement = self.organize_nameless_headers(counter, self.clean(item), first_header)
                key = f'Header__{counter}__{replacement}'

                try:
                    stop = start + int(item['colspan'])
                except KeyError:
                    stop = start + 1

                content = list(map(lambda tag: self.clean(tag), second_headers))[start:stop]
                self.headers[key] = {content[i]: "" for i in range(len(content))}
                start = stop
        else:
            self.headers = {self.clean(key): "" for key in header[0].find_all('th')}

        return self.headers

    def get_table_content(self) -> tuple:
        self.get_table_headers()
        table_body = self.get_table().tbody
        for row in table_body.find_all('tr'):
            cells = row.find_all('td')
            name = [(self.clean(row.th), row.th.a)]
            collected_data = [(self.clean(cell), cell.a) for cell in cells]
            self.data.append(self.save_data(list(itertools.chain(name, collected_data))))

        return self.get_table_title(), self.data

    def save_data(self, data) -> dict:
        data_dict = copy.deepcopy(self.headers)
        current = 0

        for key in self.headers:
            if self.double_header:
                for sub_key in self.headers[key]:
                    scrapped_item = data[current]
                    if scrapped_item[1] is not None:
                        data_dict[key][sub_key] = scrapped_item[0], f'{self.base_url}{scrapped_item[1]["href"]}'
                    else:
                        data_dict[key][sub_key] = scrapped_item[0]
                    current += 1
            else:
                scrapped_item = data[current]
                if scrapped_item[1] is not None:
                    data_dict[key] = scrapped_item[0], f'{self.base_url}{scrapped_item[1]["href"]}'
                else:
                    data_dict[key] = scrapped_item[0]
                current += 1

        return data_dict


def visualize_data(list_to_visualize):
    print('\n')
    logging.info('Instantiating data visualising module...')
    logging.info('-' * 90)
    for title, stats in list_to_visualize:
        print('\t' * 5, title)
        print('\n')
        for item in stats:
            for key, value in item.items():
                print(f'{key}: {value}')
            print('\n')
    return True


if __name__ == "__main__":

    base_url = "https://fbref.com/"
    url = f'{base_url}fr/equipes/361ca564/Statistiques-Tottenham-Hotspur'
    page_data = GetSoup(url).soup.find(id='content')

    all_data = []

    for table in page_data.find_all('div', {'class': 'table_wrapper tabbed'}):
        start_time = time.time()
        all_data.append(TableScraper(base_url, url, table['id']).get_table_content())
        end_time = time.time()
        logging.info(f'Table with id="#{table["id"]}" was scrapped in {end_time - start_time} seconds')

    # See result:
    print(visualize_data(all_data))