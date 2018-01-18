import requests
from bs4 import BeautifulSoup as bs

GENERAL_URL = 'https://www.el-com.ru/catalog/{}/'
CATEGORY = '1_kabel_provod'


def fetch_site():
    url = GENERAL_URL.format(CATEGORY)
    raw_html = requests.get(url).content
    return raw_html


def get_sub_category(content_from_site):
    pass


if __name__ == '__main__':
    content = fetch_site()
