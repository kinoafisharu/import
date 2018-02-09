import requests
import random
import re
import time
from bs4 import BeautifulSoup as bs

MAIN_URL = 'http://www.merg.ru'
KABEL = '/catalog/kabel/'
# DIR_INFO = {'catalog': CATALOG,
#             'subject': SUBJECT,}

def fetch_url(tail):
    url = MAIN_URL + tail
    timeout = (2, 10)
    agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.2a1pre) Gecko/20110324 Firefox/4.2a1pre",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:5.0) Gecko/20100101 Firefox/5.0",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:5.0) Gecko/20110619 Firefox/5.0",
    ]
    user_agent = random.choice(agent_list)
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
    headers = {'User_agent': user_agent}

    raw_html = requests.get(url, headers, timeout=timeout).content
    return raw_html


def get_soup_links(content_from_site):
    soup_content = bs(content_from_site, 'html.parser')
    soup_tag = soup_content.find('div', id='subparts')
    soup_tags = soup_tag.find_all('tr')
    soup_links = soup_tag.find_all('a')
    return soup_tags


def get_link(tag):
    link = tag.get('href')
    dict_link = {'link': link}
    return dict_link


def get_link_category(soup_with_link):
    list_link_categories = []
    for soup_tag in soup_with_link:
        soup_a = soup_tag.find_all('a')
        link_category = soup_a[1].get('href')
        dict_link_category = {'link': link_category}
        list_link_categories.append(dict_link_category)
        break
    return list_link_categories


def get_link_sub_category(list_link_categories):
    # получаем подгруппу (марка кабеля)
    list_link_sub_categories = []
    for link_category in list_link_categories:
        tail = link_category['link']
        content = fetch_url(tail)
        soup_links_sub_category = get_soup_links(content)
        description = get_description(tail)
        for soup_tag in soup_links_sub_category:
            soup_a = soup_tag.find_all('a')
            link_sub_category = soup_a[1].get('href')
            dict_link_sub_category = {'link_sub_category': link_sub_category,
                                      'description_sub_category': description}
            list_link_sub_categories.append(dict_link_sub_category)
    return list_link_sub_categories


def get_link_subject(list_link_sub_categories):
    list_link_subject = []
    for tail in list_link_sub_categories:
        subject_tail = tail['link_sub_category']
        content = fetch_url(subject_tail)
        soup_content = bs(content, 'html.parser')
        soup_tag = soup_content.find_all('a', class_='goods_a_big')
        description_sub_category = tail['description_sub_category']
        list_link_subject = []
        for tag in soup_tag:
            link_subject = tag.get('href')
            list_link_subject.append({'link_subject': link_subject,
                                      'description_sub_category': description_sub_category})
    return list_link_subject


def get_full_info(list_link_subject):
    list_full_info = []
    for subject in list_link_subject:
        tail_subject = subject['link_subject']
        subject_content = fetch_url(tail_subject)
        soup_subject = bs(subject_content, 'html.parser')
        link_chain = get_link_chain(soup_subject)
        info_subject = get_info_subject(soup_subject)
        subtag_category = link_chain['category']
        split_subtag = info_subject['title_subject'].split(' ')
        subtag_mark = split_subtag[1] + 'силовой'
        subtag_prop = split_subtag[2]
        subtag_prop_2 = split_subtag[3]
        # try:
        #     subtag_prop_2 = split_subtag[3]
        # # except:
        # #     continue
        subtag = ', '.join(split_subtag) + ', ' + subtag_category + ', ' + subtag_mark
        description = subject['description_sub_category']
        print(description)

        list_full_info.append({
            'offer_tag': 'Кабельно-проводниковая продукция',
            'offer_subtag': subtag,
            'offer_valuta': 'руб.',
            'offer_title': info_subject['title_subject'],
            'offer_price': info_subject['price'],
            'offer_value': 'м',
            "offer_minorder": '1',
            "offer_minorder_value": 'м',
            "offer_pre_text": description,
            "offer_availability": 'под заказ',
            'image_link': info_subject['image_link'],
        }
        )

    return list_full_info


def get_link_chain(soup_subject):
    chain_subject = soup_subject.find('div', id='chain')
    list_chain_links = chain_subject.find_all('a')
    group = list_chain_links[2].get_text()
    category = list_chain_links[3].get_text()
    sub_category = list_chain_links[4].get_text()
    return {
        'group': group,
        'category': category,
        'sub_category': sub_category,
        }


def get_info_subject(soup_subject):
    info_subject = soup_subject.find('div', id='good')
    title_subject = info_subject.find('div', id='g_text')
    title_subject = title_subject.find('h1').get_text()
    price = info_subject.find('div', id='g_price')
    try:
        price = price.find('b').get_text()
    except AttributeError:
        price = 'Цена по запросу'
    in_stock = info_subject.find('i').get_text()
    try:
        image_link = info_subject.find('div', id='g_big_photo')
        image_link = image_link.find('a').get('href')
        image_link = MAIN_URL + image_link
    except AttributeError:
        image_link = 'No photo'

    return {
        'title_subject': title_subject,
        'price': price,
        'in_stock': in_stock,
        'image_link': image_link,
        }


def get_description(tail):
    content = fetch_url(tail)
    soup = bs(content, 'html.parser')
    description = soup.find('i').get_text()
    print(description)
    return description


def get_output_merg():
    tail = KABEL
    content = fetch_url(tail)
    soup_with_links = get_soup_links(content)
    list_link_category = get_link_category(soup_with_links)
    list_link_sub_categories = get_link_sub_category(list_link_category)
    list_subject = get_link_subject(list_link_sub_categories)
    info_full_subject = get_full_info(list_subject)
    return info_full_subject


if __name__ == '__main__':
    tail = KABEL
    content = fetch_url(tail)
    soup_with_links = get_soup_links(content)
    list_link_category = get_link_category(soup_with_links)
    list_link_sub_categories = get_link_sub_category(list_link_category)
    list_subject = get_link_subject(list_link_sub_categories)
    # get_full_info(list_subject)
    info_full_subject = get_full_info(list_subject)
    print(info_full_subject)
