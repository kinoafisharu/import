import requests
import re

from requests.packages.urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup as bs

MAIN_URL = 'https://www.el-com.ru'
GENERAL_URL = 'https://www.el-com.ru/catalog/{}/{}/'
CATEGORY = '1_kabel_provod'
SORTED = '?CATALOG_SORT_FIELD=NAME&CATALOG_SORT_ORDER_NEW=ASC&PAGEN_1=all'
# QUERY_PARAMETER = {'CATALOG_SORT_FIELD', name}
COOKIES = dict(cityCodeNew='cr')
VARIABLE_SEARCH_CATEGORY = {'кабель': 'абел*', 'провод': 'ровод*'}


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def fetch_site():
    url = GENERAL_URL.format(CATEGORY, SORTED)
    raw_html = requests.get(url, cookies=COOKIES, verify=False).content
    return raw_html


def get_content(content_from_site):
    soup_content = bs(content_from_site, 'html.parser')
    soup_tag = soup_content.find_all('div', class_='section')
    soup_sub_tag = soup_content.find_all('div', {'class': 'one-product'})
    return soup_tag, soup_sub_tag


def get_info_tag(content_tag):
    tag_list = []
    tag_dict = {}
    sub_tag_list = []
    for tag in content_tag:
        sub_tag = get_separate_tags(tag)
        sub_tag_list.append(sub_tag)
    print(tag_list)
    return tag_list


def fetch_product_from_tag(link_tag):                                         # получает страницу с данным тегом
    raw_html = requests.get(link_tag, cookies=COOKIES, verify=False).content
    return raw_html


def get_separate_tags(tag):                                             # ищет ключевые слова и разделяет по ним теги
    print(tag)
    title_tag = tag.a.span.string
    link_tag = tag.a.get('href')
    if re.search(VARIABLE_SEARCH_CATEGORY['кабель'], title_tag):
        sub_tag = {'кабель': title_tag, 'link': (MAIN_URL+link_tag)}
    elif re.search(VARIABLE_SEARCH_CATEGORY['провод'], title_tag):
        sub_tag = {'провод': title_tag}

    return sub_tag


def get_info_product(content_sub_tag):                                  # получает необходиму информацию по продукту
    products_info = []
    for product in content_sub_tag:
        common_name = product.find('a', {'class': 'name'})
        name = common_name.get_text()
        name = ' '.join(re.findall('\w+', name))
        link_product = common_name.get('href')
        # central = product.find('span', {'class': 'central'})
        value_local = product.find('span', {'class': 'local'}).get_text()
        value_local = ''.join(re.findall('\w', value_local))
        price = product.find('span', {'class': 'price'}).get_text()
        dimension = product.find('span', {'class': 'measure'}).get_text()
        sub_tag = name
        product_dict = {'offer_title': name,
                        'offer_url': (MAIN_URL + link_product),
                        'offer_value': value_local,
                        'offer_price': price,
                        'dimension': dimension,
                        'offer_tag': '',
                        'offer_sub_tag': sub_tag,
                        }
        products_info.append(product_dict)
    return products_info


def get_output_elcom():
    data = fetch_site()
    data_category, data_sub_category = get_content(data)
    products_info = get_info_product(data_category)
    return products_info


if __name__ == '__main__':
    content = fetch_site()
    content_tag, content_sub_tag = get_content(content)
    get_info_tag(content_tag)
    link_tag = ['link']
    content_product = fetch_product_from_tag(link_tag)
    content_section_tag, content_section_sub_tag =\
        get_content(content_product)
    get_info_product(content_section_sub_tag)
