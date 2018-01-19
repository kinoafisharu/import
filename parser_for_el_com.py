import requests
import re

from requests.packages.urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup as bs

MAIN_URL = 'https://www.el-com.ru'
GENERAL_URL = 'https://www.el-com.ru/catalog/{}/{}/'
CATEGORY = '1_kabel_provod'
SORTED = '?CATALOG_SORT_FIELD=NAME&CATALOG_SORT_ORDER_NEW=ASC&PAGEN_1=all'
# QUERY_PARAMETER = {'CATALOG_SORT_FIELD'name}
COOKIES = dict(cityCodeNew='cr')

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def fetch_site():
    url = GENERAL_URL.format(CATEGORY, SORTED)
    raw_html = requests.get(url, cookies=COOKIES, verify=False).content
    return raw_html


def get_sub_category(content_from_site):
    soup_category = bs(content_from_site, 'html.parser')
    soup_sub_category = soup_category.find_all('div',
                                               {'class': 'one-product'})
    print(soup_sub_category[0])
    return soup_sub_category


def get_info_product(content_category):
    products_info = []
    for product in content_category:
        print(product)
        common_name = product.find('a', {'class': 'name'})
        name = common_name.get_text()
        name = re.findall('\w+', name)
        link = common_name.get('href')
        # central = product.find('span', {'class': 'central'})
        local = product.find('span', {'class': 'local'}).get_text()
        price = product.find('span', {'class': 'price'}).get_text()
        dimension = product.find('span', {'class': 'measure'}).get_text()
        product_dict = {'name': name,
                        'url': (MAIN_URL + link),
                        'local_warehouse': local,
                        'price': price,
                        'dimension': dimension,
                        }
        products_info.append(product_dict)
        break

    return products_info


if __name__ == '__main__':
    content = fetch_site()
    content_category = get_sub_category(content)
    print(get_info_product(content_category))
