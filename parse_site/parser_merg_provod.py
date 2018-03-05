"""
Парсинг раздела сайта merg.ru.

Скрипт  парсит и собирает данные о выбранном объекте раздела сайта
'http://www.merg.ru/catalog/provodashnur/'.

1. Для сбора информации копируется html страница каталога.
2. Проходится по всем ссылкам вглубь до товара.
3. Собираются необходимые данные о товаре (Название, цена, группа, метки,
количество на складе)
4. Подготавливаются выходные данные для конкретной базы данных.
5. Записывается pickle файл в папку /storage.

На выходе отдаётся pickle файл.
Пробное изменение Михаила
"""

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


def fetch_url(tail):
    """
    Прочитать html страницу и сохранить в память результат.

    Сервер на который делается запрос, может ставить блокировку на
    на множественные запросы. Поэтому вводятся аргументы, которые
    регулируют параметры запроса.
    :arg
        timeout - кортеж (время передачи запроса, время ожидания ответа)
        agent-list - список user-agents
        headers - параметр, который передаётся в голове запроса для того,
        чтобы завуалировать вход и прикинуться клиент-браузером.
    :param tail:
        внутренний адрес страницы сайта
    :return:
        байтовую строку
    """

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
    """
    Обработать байтовый текст и сделать первичный поиск html тегов,
    так называемый 'суп тегов'.

    :param content_from_site:
        html страницы преобразованные в байтовый текст
    :return:
        список одинаковых тегов

        ['<tr><div> Какой-то текст </div></tr>',
         '<tr><div> Какой-то текст </div></tr>',
         '<tr><div> Какой-то текст </div></tr>',
         '...',]

    """
    soup_content = bs(content_from_site, 'lxml')
    soup_tag = soup_content.find('table').find_parent('div', id='subparts')
    soup_tags = soup_tag.find_all('tr')
    return soup_tags


def get_link_category(soup_with_link):
    """
    Спарсить все ссылки на типы товаров данной страницы.

    :param soup_with_link:
        На вход подаётся 'cуп тегов'
    :return:
        Возвращает список словарей с ссылками на типы проводов с данной
        страницы
        [{'link': '/catalog/provodashnur/provod-montazhniy/'},
         {'link': '/catalog/provodashnur/provod-montazhniy/'},
         {'link': '/catalog/provodashnur/provod-montazhniy/'},
        }]
    """

    list_link_categories = []
    for soup_tag in soup_with_link:
        soup_a = soup_tag.find_all('a')
        link_category = soup_a[1].get('href')
        dict_link_category = {'link': link_category}
        list_link_categories.append(dict_link_category)
    return list_link_categories


def get_link_subcategory(link_category):
    """
    Спарсить все ссылки на подтипы товаров данной страницы.

    :param link_category:
        Словарь со ссылкой на тип провода
    :return:
        Возвращает список словарей с ссылками на подтипы проводов с данной
        страницы
        [
         {'link': '/catalog/provodashnur/provod-montazhniy/pv-puv/',
          'description_subcategory': 'описание'},
         {'link': '/catalog/provodashnur/provod-montazhniy/pv-pugv/',
          'description_subcategory': 'описание'},
         {'link': '/catalog/provodashnur/provod-montazhniy/pvs/'},
        }]
    """

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

    return list_link_subcategories


def get_link_subject(link_subcategory):
    """
    Спарсить все ссылки на товары данной страницы.

    Помимо парсинга ссылок на данной странице, формирует название файла
    и адрес, куда будет записан общий результат парсинга. Для этого
    обрабатывает ссылку на подтип провода (link_subcategory) и делает
    из неё название.

    :param link_subcategory:
        Словарь со ссылкой на тип провода
    :return:
        Возвращает кортеж (dict, str) состоящий из:
            - списка словарей с ссылками на подтипы проводов с данной
            страницы
            [
            {'link': '/catalog/provodashnur/provod-montazhniy/pv-puv/2-0-75/',
             'description_subcategory': 'описание'},
            {'link': '/catalog/provodashnur/provod-montazhniy/pv-pugv/2-0-75/',
             'description_subcategory': 'описание'},
            {'link': '/catalog/provodashnur/provod-montazhniy/pvs/2-0-75/',
             'description_subcategory': 'описание'},
            ]
            - пути с названием для сохранения файла
            'storage/catalog_provodashnur_provod-montazhniy_pvs.pickle'
    """

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


def get_full_info_provod(subject):
    """
    Подготавливает данные для вывода в файл.

    Формирует словарь с заданными ключами для вывода в файл.
    Данные берёт из словоря subject.
    Остальные данные забиты константой из-за требований, которые
    предъявляются к выходным данным.

    :param subject:
        Информация распарсенная информация о товаре
    :return:
        Возвращает словарь с необходимыми свойствами товара
        {
         'offer_tag': 'КАБЕЛЬНО-ПРОВОДНИКОВАЯ ПРОДУКЦИЯ',
         'offer_subtags': 'провода и шнуры, 2x1,5, ПВС, провод'
         'offer_valuta': 'руб.',
         'offer_title': ПВС 2x1,5,
         'offer_price': '0.0',
         'offer_value': 'м',
         'offer_minorder': '1',
         'offer_minorder_value': 'м',
         'offer_pre_text': Короткое описание товара,
         'offer_availability': 'Под заказ',
         'offer_image_url': 'http://www.merg.ru/data/icons/parts/1756_mid.png',
         'offer_url': '',
         'offer_text': 'Короткое описание товара',
         /в данной реализации используется короткое описание
         'offer_publish': '',
        }
    """

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
    full_info = {
        'offer_tag': 'КАБЕЛЬНО-ПРОВОДНИКОВАЯ ПРОДУКЦИЯ',
        'offer_subtags': subtag,
        'offer_valuta': 'руб.',
        'offer_title': info_subject['title_subject'],
        # 'offer_price': info_subject['price'], / в данной реализации не нужна реальная цена
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
    return full_info


def get_link_chain(soup_subject):
    """
    Спарсить цепочку пути (chain_subject) на товар на странице товара.
    (каталог -> Провода и шнуры -> Провод монтажный -> ПВС ->)

    Необходим для пополнения меток (свойств, описывающих товар).
    Считает что в цепочки 3 уровня, если последнего уровня нет,
    то обрабатывает ошибку и возвращает 2 уровня.
    :param soup_subject:
        Суп тегов со страницы товара.
    :return:
        Возвращает словарь {
            'group': 'Провода и шнуры',
            'category': 'Провод монтажный',
            'subcategory': 'ПВС',
        }
    """

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
    """
    Спарсить полностью страницу товара и вернуть данные.

    Проходится по всей странице товара и собирает необходимые данные о
    товаре - название, цена, количество на складе, ссылка на картинку.
    Остальные данные забиты константой из-за требований, которые
    предъявляются к выходным данным.

    :param soup_subject:
        Словарь со ссылкой на товар
    :return:
        Возвращает словарь с необходимыми свойствами товара
    """

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


def get_piсkle_goods_site():
    """
    Парсится весь подкаталог товара, например: 'Провода и шнуры'
    Логика работы прописана вверху файла.
    :return:
        Сохраняется на диск pickle файл.
    """

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
                    subject)
                list_full_info_subjects.append(full_info_subjects)      # записывает результат парсинга в pickle файл
            with open(pickle_file, 'wb') as file:
                pickle.dump(list_full_info_subjects, file,
                            pickle.HIGHEST_PROTOCOL)


def get_pickle_all_goods_category():
    """
    Парсится весь подкаталог товара, например: 'Провод монтажный'
    Логика работы прописана вверху файла.
    Вводится переменная url_category для отсеивания
    необходимой для парсинга категории товара.
    :args:
        url_category - ссылка на необходимую категорию товара
    :return:
        Сохраняется на диск pickle файл.
    """

    tail = PROVOD
    url_category = '/catalog/provodashnur/provod-montazhniy/'
    content = fetch_url(tail)
    soup_with_links = get_soup_links(content)
    list_link_categories = get_link_category(soup_with_links)
    for link_category in list_link_categories:
        if link_category['link'] == url_category:
            # ищет нужную категорию
            try:
                # проверяет страницу как подкатегорию товара
                list_link_subcategories = get_link_subcategory(
                    link_category)
                for link_subcategory in list_link_subcategories:
                    list_subjects, pickle_file = get_link_subject(
                        link_subcategory)
                    list_full_info_subjects = []
                    for subject in list_subjects:
                        full_info_subjects = get_full_info_provod(
                            subject)
                        list_full_info_subjects.append(
                            full_info_subjects)
                    if list_full_info_subjects:
                        with open(pickle_file, 'wb') as file:
                            pickle.dump(list_full_info_subjects, file,
                                        pickle.HIGHEST_PROTOCOL)
                            # записывает результат парсинга в pickle
                            # файл
            except AttributeError:
                # при ошибке начинается парсинг страницы, как список
                # товара
                list_subjects, pickle_file = get_link_subject(
                    link_category)
                list_full_info_subjects = []
                for subject in list_subjects:
                    # проходит по этому списку
                    full_info_subjects = get_full_info_provod(
                        subject)
                    list_full_info_subjects.append(full_info_subjects)
                if list_full_info_subjects:
                    with open(pickle_file, 'wb') as file:
                        pickle.dump(list_full_info_subjects, file,
                                    pickle.HIGHEST_PROTOCOL)
                        # записывает результат парсинга в pickle файл
        else:
            continue


def get_pickle_all_goods_subcategory():
    """
    Парсится весь под подкаталог товара, например: 'ПВС'
    Логика работы прописана вверху файла.
    Вводится переменная url_subcategory для отсеивания
    необходимой для парсинга подкатегории товара.
    :args:
        url_subcategory - ссылка на необходимую подкатегорию товара
    :return:
        Сохраняется на диск pickle файл.
    """

    tail = PROVOD
    url_subcategory = '/catalog/provodashnur/provod-montazhniy/pvs/'
    content = fetch_url(tail)
    soup_with_links = get_soup_links(content)
    list_link_categories = get_link_category(soup_with_links)
    for link_category in list_link_categories:
        try:
            list_link_subcategories = get_link_subcategory(link_category)
            for link_subcategory in list_link_subcategories:
                if link_subcategory['link'] == url_subcategory:
                    list_subjects, pickle_file = get_link_subject(
                        link_subcategory)
                    list_full_info_subjects = []
                    for subject in list_subjects:
                        full_info_subjects = get_full_info_provod(
                           subject)
                        list_full_info_subjects.append(
                           full_info_subjects)
                    with open(pickle_file, 'wb') as file:
                        pickle.dump(list_full_info_subjects, file,
                                    pickle.HIGHEST_PROTOCOL)
                else:
                    continue
        except AttributeError:
            continue


def get_pickle_good():
    """
    Парсится товар, например: 'ПВС 2 х 0,75'
    Логика работы прописана вверху файла.
    Вводится переменная url_subcategory для отсеивания
    необходимой для парсинга подкатегории товара.
    :args:
        url_subject - ссылка на необходимый товар
    :return:
        Сохраняется на диск pickle файл.
    """

    tail = SIP
    url_subject = '/catalog/provod-sip/2/16/'
    content = fetch_url(tail)
    soup_with_links = get_soup_links(content)
    list_link_categories = get_link_category(soup_with_links)
    for link_category in list_link_categories:
        try:
            list_link_subcategories = get_link_subcategory(link_category)
            for link_subcategory in list_link_subcategories:
                list_subjects, pickle_file = get_link_subject(
                    link_subcategory)
                list_full_info_subjects = []
                for subject in list_subjects:
                    full_info_subjects = get_full_info_provod(
                        subject)
                    if subject['link'] == url_subject:
                        list_full_info_subjects.append(full_info_subjects)
                    else:
                        continue
                if list_full_info_subjects:
                    with open(pickle_file, 'wb') as file:
                        pickle.dump(list_full_info_subjects, file,
                                    pickle.HIGHEST_PROTOCOL)

        except AttributeError:
            list_subjects, pickle_file = get_link_subject(
                link_category)
            list_full_info_subjects = []
            for subject in list_subjects:
                full_info_subjects = get_full_info_provod(
                    subject)
                if subject['link'] == url_subject:
                    list_full_info_subjects.append(
                        full_info_subjects)
                else:
                    continue
            if list_full_info_subjects:
                with open(pickle_file, 'wb') as file:
                    pickle.dump(list_full_info_subjects, file,
                                pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    get_pickle_good()
