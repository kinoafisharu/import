import requests
import re

from bs4 import BeautifulSoup as bs

MAIN_URL = 'http://www.merg.ru/'
KABEL = 'catalog/kabel/'
# DIR_INFO = {'catalog': CATALOG,
#             'subject': SUBJECT,}

def fetch_url(tail):
    url = MAIN_URL + tail
    raw_html = requests.get(url).content
    return raw_html


def get_info_category(content_from_site):
    list_info_categories = []
    soup_content = bs(content_from_site, 'html.parser')
    soup_tag = soup_content.find('div', id='subparts')
    links_category = soup_tag.find_all('a')

    for data in links_category:
        link_category = data.get('href')
        try:
            title_category = data.find('img').get('title')
            link_image_category = data.find('img').get('src')
        except AttributeError:
            continue
        dict_info_category = {'title': title_category,
                              'link': link_category,
                              'link_image': link_image_category}
        list_info_categories.append(dict_info_category)
        break

    return list_info_categories


def get_info_sub_category(list_categories):
    list_subs_category = []
    list_main = []
    for category in list_categories:
        tail = category['link']
        content = fetch_url(tail)
        list_sub = get_info_category(content)
        dict_subs = {category['title']: list_sub}
        dict_with_main = {'кабель': list_sub}
        list_subs_category.append(dict_subs)
        list_main.append(dict_with_main)

    return list_subs_category, list_main


def get_info_subject(common_list):
    for sub_category in common_list:
        final_list = []
        for tail in sub_category['кабель']:
            list_common_subject = []
            sub_tail = tail['link']
            content = fetch_url(sub_tail)
            soup_content = bs(content, 'html.parser')
            soup_tag = soup_content.find_all('a', class_='goods_a_big')
            list_subject = get_subject(soup_tag)
            for subject in list_subject:
                list_info_subject = []
                tail_subject = subject['link_subject']
                subject_content = fetch_url(tail_subject)
                soup_subject = bs(subject_content, 'html.parser')
                info_subject = soup_subject.find('div', id='goods')
                print(info_subject)
                title_subject = info_subject.find('h1').get_text
                price = info_subject.find('b').get_text()
                in_stock = info_subject.find('strong').get_text()
                try:
                    image_link = info_subject.find('a').get('href')
                except AttributeError:
                    image_link = 'No photo'
                list_info_subject.append({'title_subject': title_subject,
                                          'price': price,
                                          'in_stock': in_stock,
                                          'dimension': 'м',
                                          'image_link': image_link})
            list_common_subject.append({list_subject['title']: list_info_subject})
        final_list.append({sub_category: list_common_subject})



    return


def get_subject(soup_tag):
    list_subject = []
    for tag in soup_tag:
        title_subject = tag.get('title')
        link_subject = tag.get('href')
        print(link_subject)
        list_subject.append({'title_subject': title_subject,
                             'link_subject': link_subject})
    return list_subject


if __name__ == '__main__':
    tail = KABEL
    content = fetch_url(tail)
    content_tag = get_info_category(content)
    list_common, list_main = get_info_sub_category(content_tag)
    print(get_info_subject(list_main))

