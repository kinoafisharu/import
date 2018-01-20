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


def get_content_category(content_from_site):
    soup_content = bs(content_from_site, 'html.parser')
    soup_category = soup_content.find('div', {'class': 'h1'})
    soup_sub_category = soup_content.find_all('div',
                                               {'class': 'one-product'})
    return soup_category, soup_sub_category


def get_info_product(content_category, content_sub_category):
    products_info = []
    tag = content_category.find('h1').get_text()
    tag = re.findall('\D+', tag)
    print(tag)
    for product in content_sub_category:
        common_name = product.find('a', {'class': 'name'})
        name = common_name.get_text()
        name = ' '.join(re.findall('\w+', name))
        link = common_name.get('href')
        # central = product.find('span', {'class': 'central'})
        value_local = product.find('span', {'class': 'local'}).get_text()
        value_local = ''.join(re.findall('\w', value_local))
        price = product.find('span', {'class': 'price'}).get_text()
        dimension = product.find('span', {'class': 'measure'}).get_text()
        sub_tag = name
        product_dict = {'offer_title': name,
                        'offer_url': (MAIN_URL + link),
                        'offer_value': value_local,
                        'offer_price': price,
                        'dimension': dimension,
                        'offer_tag': tag,
                        'offer_sub_tag': sub_tag,
                        }
        products_info.append(product_dict)
    return products_info


def output_products():
    data = fetch_site()
    data_category, data_sub_category = get_content_category(data)
    products_info = get_info_product(data_category, data_sub_category)
    return products_info


if __name__ == '__main__':
    content = fetch_site()
    content_category, content_sub_category = get_content_category(content)
    get_info_product(content_category, content_sub_category)
