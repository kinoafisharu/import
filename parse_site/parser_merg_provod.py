import requests
import random
import pickle
from bs4 import BeautifulSoup as bs


MAIN_URL = 'http://www.merg.ru'
TYPE_OBJECT = dict(
    type_object=[{'kabel': '/catalog/kabel/',
                  'provod': '/catalog/provodashnur/',
                  'sip': '/catalog/provod-sip/'}])

KABEL = '/catalog/kabel/'
PROVOD = '/catalog/provodashnur/'
SIP = '/catalog/provod-sip/'
# DIR_INFO = {'catalog': CATALOG,
#             'subject': SUBJECT,}


def fetch_url(tail):
    # Запрос к странице n-ого уровня по адресу url с возвращением ответа (страницы)

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
    # Обработка ответа из fetch_url и получение 'супа' с ссылками на
    # страницы n уровня

    soup_content = bs(content_from_site, 'lxml')
    soup_tag = soup_content.find('table').find_parent('div', id='subparts')
    # soup_tag = soup_tag.find('table')
    soup_tags = soup_tag.find_all('tr')
    return soup_tags


# def get_link(tag):
#     link = tag.get('href')
#     dict_link = {'link': link}
#     return dict_link


def get_link_category(soup_with_link):
    # Получает ссылки со страницы 2 уровня на подгруппы (тип кабеля) и
    #  возвращает список этих ссылок

    list_link_categories = []
    for soup_tag in soup_with_link:
        soup_a = soup_tag.find_all('a')
        link_category = soup_a[1].get('href')
        dict_link_category = {'link': link_category}
        list_link_categories.append(dict_link_category)
    return list_link_categories


def get_link_subcategory(link_category):
    # Получает ссылки со странцы 3 уровня на подгруппу (марка кабеля) и
    #  возвращает список этих ссылок

    list_link_subcategories = []
    tail = link_category['link']
    content = fetch_url(tail)
    soup_links_subcategory = get_soup_links(content)
    for soup_tag in soup_links_subcategory:
        soup_a = soup_tag.find_all('a')
        link_subcategory = soup_a[1].get('href')
        try:
            description = soup_a[2].find('i').get_text()
        except IndexError:
            description = ''
        dict_link_subcategory = {'link': link_subcategory,
                                  'description_subcategory': description}
        list_link_subcategories.append(dict_link_subcategory)
    #
    # name_file = link_subcategory.split('/')
    # name_file = name_file[1:-1]
    # name_file = '_'.join(name_file)
    # pickle_file = 'storage/{}.pickle'.format(name_file)

    return list_link_subcategories


def get_link_subject(link_subcategory):
    # Получает ссылки со страницы 4 уровня на кабели (товар) и возвращает список этих ссылок

    list_link_subject = []
    subject_tail = link_subcategory['link']
    content = fetch_url(subject_tail)
    soup_content = bs(content, 'html.parser')
    soup_tag = soup_content.find_all('a', class_='goods_a_big')
    try:
        description_subcategory = link_subcategory['description_subcategory']
    except KeyError:
        description_subcategory = ''
    for tag in soup_tag:
        link_subject = tag.get('href')
        list_link_subject.append({'link': link_subject,
                                  'description_subcategory': description_subcategory})

    name_file = link_subcategory['link'].split('/')
    name_file = name_file[1:-1]
    name_file = '_'.join(name_file)
    pickle_file = 'storage/{}.pickle'.format(name_file)

    return list_link_subject, pickle_file


def get_full_info_provod(subject, link_subcategory):
    # Проходит по ссылкам и получает полную информацию о ПРОВОДЕ (товаре)
    # Записывает результат в pickle файл для последующей конвертации в json

    list_full_info = []
    tail_subject = subject['link']
    subject_content = fetch_url(tail_subject)
    soup_subject = bs(subject_content, 'html.parser')
    link_chain = get_link_chain(soup_subject)
    info_subject = get_info_subject(soup_subject)
    subtag_category = link_chain['category']
    split_subtag = info_subject['title_subject'].split(' ')
    subtag_mark = 'Провода и шнуры'
    subtag = ', '.join(split_subtag) + ', ' + subtag_category + ', ' + subtag_mark
    description = subject['description_subcategory']
    list_full_info.append({
        'offer_tag': 'КАБЕЛЬНО-ПРОВОДНИКОВАЯ ПРОДУКЦИЯ',
        'offer_subtags': subtag,
        'offer_valuta': 'руб.',
        'offer_title': info_subject['title_subject'],
        # 'offer_price': info_subject['price'],
        'offer_price': '0.0',
        'offer_value': 'м',
        'offer_minorder': '1',
        'offer_minorder_value': 'м',
        'offer_pre_text': description,
        'offer_availability': 'Под заказ',
        'offer_image_url': info_subject['image_link'],
        'offer_url': '',
        'offer_text': description,
        'offer_publish': '',
    }
    )
    name_file = link_subcategory['link'].split('/')
    name_file = name_file[1:-1]
    name_file = '_'.join(name_file)

    pickle_file = 'storage/{}.pickle'.format(name_file)
    with open(pickle_file, 'wb') as file:
        pickle.dump(list_full_info, file, pickle.HIGHEST_PROTOCOL)
    return list_full_info


def get_link_chain(soup_subject):
    # Распарсивает цепочку (дерево) категорий и подкатегорий на странице
    # объекта и возвращает словарь

    chain_subject = soup_subject.find('div', id='chain')
    list_chain_links = chain_subject.find_all('a')
    group = list_chain_links[2].get_text()
    category = list_chain_links[3].get_text()
    try:
        subcategory = list_chain_links[4].get_text()
        return {
            'group': group,
            'category': category,
            'subcategory': subcategory,
        }
    except IndexError:
        return {
            'group': group,
            'category': category,
        }


def get_info_subject(soup_subject):
    # Распарсивает необходимые данные на странице объекта и возвращает
    # словарь с этими данными

    info_subject = soup_subject.find('div', id='good')
    title_subject = info_subject.find('div', id='g_text')
    title_subject = title_subject.find('h1').get_text()
    price = info_subject.find('div', id='g_price')
    try:
        price = price.find('b').get_text()
    except AttributeError:
        price = 0.00
    in_stock = info_subject.find('i').get_text()
    try:
        image_link = info_subject.find('div', id='g_big_photo')
        image_link = image_link.find('a').get('href')
        image_link = MAIN_URL + image_link
    except AttributeError:
        image_link = ''

    return {
        'title_subject': title_subject,
        'price': price,
        'in_stock': in_stock,
        'image_link': image_link,
        }


def get_description(tail):
    # Распарсивает страницу 3 уровня, и получает короткое описание объекта

    content = fetch_url(tail)
    soup = bs(content, 'html.parser')
    description = soup.find('i').get_text()
    return description


def get_output_merg():
    # Запускает парсинг всех объектов находящихся на 2 уровне и в глубь

    tail = PROVOD                                                       # определяет начало url для парсинга (в данном случае силовой кабель)
    content = fetch_url(tail)                                           # получает контент страницы 2 уровня
    soup_with_links = get_soup_links(content)                           # получает обработанный bs4 'суп'
    list_link_category = get_link_category(soup_with_links)             # получает список ссылок на страницы 3 уровня
    for link_category in list_link_category:                            # проходит по каждой ссылке списка
        list_link_subcategories, pickle_file = get_link_subcategory(link_category)   # получает список ссылок на странице 4 уровня
        for link_subcategory in list_link_subcategories:                # проходит по этому списку
            list_subjects = get_link_subject(
                link_subcategory)                                       # получает список ссылок на объекты (страница 5 уровня)
            list_full_info_subjects = []
            for subject in list_subjects:                               # проходит по этому списку
                full_info_subjects = get_full_info_provod(
                    subject, link_subcategory)
                list_full_info_subjects.append(full_info_subjects)      # записывает результат парсинга в pickle файл
            with open(pickle_file, 'wb') as file:
                pickle.dump(list_full_info_subjects, file,
                            pickle.HIGHEST_PROTOCOL)

            break


def get_output_category():
    # Запускает парсинг всех объектов находящихся на 3 уровне и в глубь
    # Необходимо передать в переменную url_category - something
    # Пример - /catalog/provod/rezinovoj/

    tail = PROVOD
    url_category = '/catalog/provodashnur/*/'
    content = fetch_url(tail)
    soup_with_links = get_soup_links(content)
    list_link_categories = get_link_category(soup_with_links)
    for link_category in list_link_categories:
        if link_category['link'] == url_category:        # ищет нужную категорию
            try:
                list_link_subcategories = get_link_subcategory(
                    link_category)
                for link_subcategory in list_link_subcategories:  # ищет нужный кабель
                    list_subjects, pickle_file = get_link_subject(
                        link_subcategory)
                    list_full_info_subjects = []
                    for subject in list_subjects:  # проходит по этому списку
                        full_info_subjects = get_full_info_provod(
                            subject, link_subcategory)
                        list_full_info_subjects.append(
                            full_info_subjects)  # записывает результат парсинга в pickle файл
                    if list_full_info_subjects:
                        with open(pickle_file, 'wb') as file:
                            pickle.dump(list_full_info_subjects, file,
                                        pickle.HIGHEST_PROTOCOL)
            except AttributeError:
                list_subjects, pickle_file = get_link_subject(
                    link_category)
                list_full_info_subjects = []
                for subject in list_subjects:  # проходит по этому списку
                    full_info_subjects = get_full_info_provod(
                        subject, link_category)
                    list_full_info_subjects.append(full_info_subjects)  # записывает результат парсинга в pickle файл
                if list_full_info_subjects:
                    with open(pickle_file, 'wb') as file:
                        pickle.dump(list_full_info_subjects, file,
                                    pickle.HIGHEST_PROTOCOL)

        else:
            continue


def get_output_subcategory():
    # Запускает парсинг всех объектов находящихся на 4 уровне и в глубь
    # Необходимо передать в переменную url_subcategory - something
    # Пример - /provod/rezinovoj/kg/

    tail = PROVOD
    url_subcategory = '/catalog/provodashnur/*/*/'
    content = fetch_url(tail)
    soup_with_links = get_soup_links(content)
    list_link_categories = get_link_category(soup_with_links)
    for link_category in list_link_categories:
        try:
            list_link_subcategories = get_link_subcategory(link_category)
            for link_subcategory in list_link_subcategories:
                if link_subcategory['link'] == url_subcategory: # ищет нужный вид кабеля
                    list_subjects, pickle_file = get_link_subject(
                        link_subcategory)
                    list_full_info_subjects = []
                    for subject in list_subjects:                           # проходит по этому списку
                        full_info_subjects = get_full_info_provod(
                           subject, link_subcategory)
                        list_full_info_subjects.append(
                           full_info_subjects)                             # записывает результат парсинга в pickle файл
                    with open(pickle_file, 'wb') as file:
                        pickle.dump(list_full_info_subjects, file,
                                    pickle.HIGHEST_PROTOCOL)
                else:
                    continue
        except AttributeError:
            continue

def get_output_subject():
    # Запускает парсинг всех объектов находящихся на 5 уровне
    # Необходимо передать в переменную url_subject - something
    # Пример - /catalog/provod/rezinovoj/kg/1-10/

    tail = PROVOD
    url_subject = '/catalog/provodashnur/provod-montazhniy/pv-pugv/17995/'
    content = fetch_url(tail)
    soup_with_links = get_soup_links(content)
    list_link_categories = get_link_category(soup_with_links)
    for link_category in list_link_categories:
        try:
            list_link_subcategories = get_link_subcategory(link_category)
            for link_subcategory in list_link_subcategories:                # ищет нужный кабель
                list_subjects, pickle_file = get_link_subject(
                    link_subcategory)
                list_full_info_subjects = []
                for subject in list_subjects:  # проходит по этому списку
                    full_info_subjects = get_full_info_provod(
                        subject, link_subcategory)
                    if subject['link'] == url_subject:
                        list_full_info_subjects.append(full_info_subjects)  # записывает результат парсинга в pickle файл
                    else:
                        continue
                if list_full_info_subjects:
                    with open(pickle_file, 'wb') as file:
                        pickle.dump(list_full_info_subjects, file,
                                    pickle.HIGHEST_PROTOCOL)

        except AttributeError:                                             # ищет нужный кабель
            list_subjects, pickle_file = get_link_subject(
                link_category)
            list_full_info_subjects = []
            for subject in list_subjects:  # проходит по этому списку
                full_info_subjects = get_full_info_provod(
                    subject, link_category)
                if subject['link'] == url_subject:
                    list_full_info_subjects.append(
                        full_info_subjects)  # записывает результат парсинга в pickle файл
                else:
                    continue
            if list_full_info_subjects:
                with open(pickle_file, 'wb') as file:
                    pickle.dump(list_full_info_subjects, file,
                                pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    get_output_subject()
