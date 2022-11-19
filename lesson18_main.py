import json
import re
from collections import Counter

import requests

import pprint

# DOMAIN = 'https://api.hh.ru/'

'''
Словарь с городами выглядит примерно так:
[{'areas': [{'areas': [{'areas': [],             - это для городов входящих
                        'id': '4228',              в конкретный субъект РФ
                        'name': 'Виловатово',
                        'parent_id': '1620'},
                       {'areas': [],
                        'id': '1621',
                        'name': 'Волжск',
                        'parent_id': '1620'},
                         ..............  - тут много других данных
             'id': '1620',                  - это для субъектов РФ.
             'name': 'Республика Марий Эл',
             'parent_id': '113'},
            {'areas': [],                   - это для городов федерального значения.
             'id': '1',                       То есть, когда город является одновременно 
             'name': 'Москва',                и субъектом РФ.
             'parent_id': '113'},
            {'areas': [{'areas': [],
                        'id': '1625',
                        'name': 'Агрыз',
                        'parent_id': '1624'},
                       {'areas': [],
                        'id': '1626',
                        'name': 'Азнакаево',
                        'parent_id': '1624'},
                         ..............  - тут много других данных
             'id': '1624',
             'name': 'Республика Татарстан',
             'parent_id': '113'},
             ..............  - тут много других данных
  'id': '113',
  'name': 'Россия',
  'parent_id': None},
 {'areas': [{'areas': [{'areas': [],
                        'id': '3331',
                        'name': 'Бар',
                        'parent_id': '2121'},
                         ..............  - тут много других данных
  'id': '5',
  'name': 'Украина',
  'parent_id': None},
  ..............  - и далее по разным странам СНГ

Описание полей:
https://github.com/hhru/api/blob/master/docs/vacancies.md#vacancy-fields

Словарь с вакансиями выглядит так:

Параметры запроса:
params = {
    'text': 'NAME:(Python OR Java) AND (DJANGO OR SPRING)',
    'area': 1,
    # есть страницы т.к. данных много
    'per_page': 1
}
response = requests.get('https://api.hh.ru/vacancies', params=params).json()

{'alternate_url': 'https://hh.ru/search/vacancy?area=1&control_flag=vacancyBlacklistJoinEnabled%3ATrue&enable_snippets=true&items_on_page=1&text=NAME%3A%28Python+OR+Java%29+AND+%28DJANGO+OR+SPRING%29',
 'arguments': None,
 'clusters': None,
 'found': 870,
 'items': [{'accept_temporary': False,
            'address': {'building': None,
                        'city': None,
                        'description': None,
                        'id': '3734130',
                        'lat': None,
                        'lng': None,
                        'metro': {'lat': 55.772315,
                                  'line_id': '6',
                                  'line_name': 'Калужско-Рижская',
                                  'lng': 37.63285,
                                  'station_id': '6.137',
                                  'station_name': 'Сухаревская'},
                        'metro_stations': [{'lat': 55.772315,
                                            'line_id': '6',
                                            'line_name': 'Калужско-Рижская',
                                            'lng': 37.63285,
                                            'station_id': '6.137',
                                            'station_name': 'Сухаревская'}],
                        'raw': None,
                        'street': None},
            'adv_response_url': 'https://api.hh.ru/vacancies/39736489/adv_response?host=hh.ru',
            'alternate_url': 'https://hh.ru/vacancy/39736489',
            'apply_alternate_url': 'https://hh.ru/applicant/vacancy_response?vacancyId=39736489',
            'archived': False,
            'area': {'id': '1',
                     'name': 'Москва',
                     'url': 'https://api.hh.ru/areas/1'},
            'contacts': None,
            'created_at': '2022-09-11T23:44:34+0300',
            'department': None,
            'employer': {'alternate_url': 'https://hh.ru/employer/4596113',
                         'id': '4596113',
                         'logo_urls': {'240': 'https://hhcdn.ru/employer-logo/3373013.png',
                                       '90': 'https://hhcdn.ru/employer-logo/3373012.png',
                                       'original': 'https://hhcdn.ru/employer-logo-original/732984.png'},
                         'name': 'Фабрика Решений',
                         'trusted': True,
                         'url': 'https://api.hh.ru/employers/4596113',
                         'vacancies_url': 'https://api.hh.ru/vacancies?employer_id=4596113'},
            'has_test': False,
            'id': '39736489',
            'insider_interview': None,
            'name': 'Python-разработчик (Django, DRF)',
            'premium': False,
            'published_at': '2022-09-11T23:44:34+0300',
            'relations': [],
            'response_letter_required': False,
            'response_url': None,
            'salary': {'currency': 'RUR',
                       'from': 60000,
                       'gross': False,
                       'to': 150000},
            'schedule': {'id': 'remote', 'name': 'Удаленная работа'},
            'snippet': {'requirement': 'Опыт разработки сложных проектов. '
                                       'Обязателен опыт работы с '
                                       '<highlighttext>django</highlighttext> '
                                       '2.*, python 3.7, djangorestframework. '
                                       'Знание SQL (в частности, PostgreSQL) '
                                       'и...',
                        'responsibility': 'Внимание: с командами не работаем, '
                                          'только с индивидуальными '
                                          'исполнителями. Профессиональный '
                                          'рост и участие в построении '
                                          'архитектур сложных систем.'},
            'sort_point_distance': None,
            'type': {'id': 'open', 'name': 'Открытая'},
            'url': 'https://api.hh.ru/vacancies/39736489?host=hh.ru',
            'working_days': [],
            'working_time_intervals': [],
            'working_time_modes': []}],
 'page': 0,
 'pages': 870,
 'per_page': 1}


Параметр 'salary' может иметь такие варианты
 - вообще не заполнен,
 - заполнены оба параметра ОТ и ДО,
 - заполнен только один параметр - или ОТ, или ДО
salary           object или null     Оклад
salary.from      number или null     Нижняя граница вилки оклада
salary.to        number или null     Верняя граница вилки оклада
salary.gross     boolean или null    Признак того что оклад указан до вычета налогов. 
                                     В случае если не указано - null.
salary.currency  string              Идентификатор валюты оклада (справочник currency).
                                     https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/paths/~1dictionaries/get
'salary': None,
'salary': {'currency': 'RUR',
           'from': 60000,
           'gross': False,
           'to': 150000},
'salary': {'currency': 'RUR',
           'from': 100000,
           'gross': False,
           'to': None},
'salary': {'currency': 'RUR',
           'from': None,
           'gross': False,
           'to': 220000},
параметр 'currency' может быть: 'RUR', 'EUR', "USD", "BYR", "AZN", и прочее
Подробнее: https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/paths/~1dictionaries/get


В полученном списке вакансий интересуют такие параметры:
- 'alternate_url': 'https://hh.ru/vacancy/39736489',
  это ссылка на представление вакансии на сайте
- 'url': 'https://api.hh.ru/vacancies/39736489?host=hh.ru',
  это ссылка на полные данные о конкретной вакансии
url и alternate_url могут принимать значение null в случае, если подробная 
информация о вакансии недоступна (например, вакансия была удалена).

Получив полное описание вакансии по ссылке 'url': 'https://api.hh.ru/vacancies/39736489?host=hh.ru'
смотрим такие поля:
- description. Тип: string
  Описание вакансии, содержит html 
- key_skills. Тип: array
  Информация о ключевых навыках, заявленных в вакансии. Список может быть пустым. 
- key_skills[].name. Тип: string
  название ключевого навыка 

Пример:
 'description': '<p>Привет! Мы, студия fabrique, ищем классного junior или '
                'middle backend-разработчика на python (работа в офисе в '
                'Москве или удаленный фулл-тайм). Мы автоматизируем '
                'бизнес-процессы крупных заказчиков, создавая удобные и '
                'выверенные сервисы. В работе множество сложных, в том числе '
                'высоконагруженных, проектов, широкий спектр интересных '
                'задач.</p> <p>Основные технологии проекта: Django 2.2, DRF, '
                'PostgreSQL.</p> <p><strong>Требования:</strong></p> <ul> '
                '<li>Опыт веб-разработки от одного года, программирования не '
                'менее трёх лет.</li> <li>Умение разбираться в чужом '
                'коде.</li> <li>Опыт разработки сложных проектов.</li> '
                '<li>Обязателен опыт работы с django 2.*, python 3.7, '
                'djangorestframework</li> <li>Знание SQL (в частности, '
                'PostgreSQL) и умение оптимизировать запросы.</li> <li>Умение '
                'составлять сложные SQL-запросы</li> <li>Знание регулярных '
                'выражений.</li> <li>Знание HTML/CSS/JS на базовом '
                'уровне.</li> <li>Английский язык на техническом уровне.</li> '
                '</ul> <p>Внимание: с командами не работаем, только с '
                'индивидуальными исполнителями.</p> '
                '<p><strong>Бонусы:</strong></p> <ul> <li>Удалённая работа в '
                'комфортное время</li> <li>Профессиональный рост и участие в '
                'построении архитектур сложных систем</li> </ul> <p><strong>В '
                'комментарии к отклику, пожалуйста, оставляйте свой ник в '
                'телеграме.</strong></p>',
 'key_skills': [{'name': 'Python'},
                {'name': 'Django Framework'},
                {'name': 'PostgreSQL'},
                {'name': 'SQL'},
                {'name': 'CSS'},
                {'name': 'Git'},
                {'name': 'RabbitMQ'}],


Возможно, что не все навыки из description будут включаться в  key_skills.
Например, в описании имеются "Знание HTML/CSS/JS". А в key_skills указано только "CSS".

Поэтому будем выбирать все английские слова, которые:
- начинаются с пробела: 
  \s — совпадает с пробельными символами (\t, \n, \r, \f и пробелом).
- содержат латинские буквы в любом регистре и символ тире ("-"):
  [A-Za-z-?]+
- через пробел (или несколько) могут заканчиваться на цифры, после которых могут 
  идти или символ "*" или цифры: Django   2332.25.87.*.*.8
  То есть, такая конструкция может встречаться, а может и отсутствовать.
  \s+(\d+(\.(\d+|\*))*)? 
 - заканчивается пробелом или тире ("-")

пример:
из фразы "или middle backend-разработчика на python " будет выбрано:
 - "middle "
 - "backend-"
 - "python "

Теряются конструкции: HTML/CSS/JS
Но при этом не ловятся конструкции типа html-тегов: </li> и <li>

Таким образом, будут выбираться версии требований:
- Django 3.*
- Django 3.1
- Django 2.*

это всё будут различные навыки.


Итоговое регулярное выражение (проверка онлайн: https://regex101.com/ ):
\s[A-Za-z-?]+-?(?:\s+\d+(?:\.(?:\d+|\*))*)? 
  Пояснение:
  ( https://habr.com/ru/post/349860/?ysclid=l7ymfl4bq8118369293 )
  - \s — совпадает с пробельными символами (\t, \n, \r, \f и пробелом)
  - bar+ — соответствует 1 или более вхождениям "bar".
  - foo* — соответствует 0 или более вхождений "foo".
  - foo? — соответствует 0 или 1 вхождению "foo".
  - [4fw] — соответствует любому из символов в скобках.
  - A-Z - символы от "A" до "Z"
  - \d - десятичная цифра. Аналог: [0-9]
  - \. - символ точка (".")
  - \* - символ звёздочка ("*")
  - скобки (?:...) позволяют локализовать часть шаблона, внутри которого происходит перечисление.
    Если  писать круглые скобки и без значков ?:, то от этого у группировки значительно 
    меняется смысл.
    Итак, если REGEXP — шаблон, то (?:REGEXP) — эквивалентный ему шаблон. Разница только 
    в том, что теперь к (?:REGEXP) можно применять квантификаторы, указывая, сколько именно 
    раз должна повториться группа.

'''


def get_city(domain='https://api.hh.ru/', city_name='Москва'):
    # определяем город, в котором ищем вакансии
    # city теоретически надо запрашивать у пользователя,
    # поэтому закладываем обработки ввода.
    city_id = None
    parent_id = None
    city = city_name.capitalize().strip()  # .strip() - обрезает пробелы
    # теоретически, надо добавить все не нужные
    # символы (кроме букв, цифр и тире)
    # .capitalize() - меняет на заглавную букву
    # только первый символ строки
    # .lower() - переводит строку в нижний регистр

    url_areas = f'{domain}areas'
    result = requests.get(url_areas).json()

    for i in result[0]['areas']:
        if city == i['name'].capitalize():
            # Перебор всех субъектов.
            # На случай ошибки в базе преобразуем строку к нужному регистру
            # проверяем на случай города федерального значения
            city_id = i['id']  # Идентификатор города
            parent_id = i['parent_id']  # Идентификатор вышестоящего субъекта
            # (Россия для городов федерального значения)
            break
        for j in i['areas']:
            # Перебор всех городов в конкретном субъекте
            # На случай ошибки в базе преобразуем строку к нужному регистру
            if city == j['name'].capitalize():
                city_id = j['id']  # Идентификатор города
                parent_id = j['parent_id']  # Идентификатор вышестоящего субъекта
                # (наименование субъекта для простых городов)
                break
    print('city_name:', city)
    print('city_id:', city_id)
    print('parent_id:', parent_id)
    return city_id, city, parent_id


# Ищем вакансии
def searching_vacancies(city_name='Москва',
                        vacancies_name='Python OR Java',
                        vacancies_description='DJANGO OR SPRING',
                        domain='https://api.hh.ru/'):
    url_vacancies = f'{domain}vacancies'
    '''
    text — текстовое поле.
        Переданное значение ищется в полях вакансии, указанных в параметре search_field.
        Доступен язык запросов, как и на основном сайте: https://hh.ru/article/1175. 
        Специально для этого поля есть автодополнение.
        
    area — регион. Необходимо передавать id из справочника /areas.
        Возможно указание нескольких значений.
    
    currency — код валюты.
        Справочник с возможными значениями: currency (ключ code) в /dictionaries.
        Имеет смысл указывать только совместно с параметром salary.
    
    salary — размер заработной платы.
        Если указано это поле, но не указано currency, то используется значение RUR у currency.
        При указании значения будут найдены вакансии, в которых вилка зарплаты близка 
        к указанной в запросе. При этом значения пересчитываются по текущим курсам ЦБ РФ. 
        Например, при указании salary=100&currency=EUR будут найдены вакансии, где вилка 
        зарплаты указана в рублях и после пересчёта в Евро близка к 100 EUR. По умолчанию 
        будут также найдены вакансии, в которых вилка зарплаты не указана, чтобы такие 
        вакансии отфильтровать, используйте only_with_salary=true.
    '''
    count_vacancies = 0  # Общее количество обработанных вакансий
    salary = {}  # Сумма зарплат. Словарь, в котором
    # наименование валюты является ключом
    count = {}  # Количество вакансий, где указана зарплата.
    # Словарь, в котором наименование валюты является ключом
    count_None = 0  # Количество вакансий, где зарплата не указана

    # city_name = 'Москва'   # Тут должен стоять ввод через input:
    #                        # city_name = input('Введите город для поиска вакансий')
    city_id, city, parent_id = get_city(domain, city_name)
    # vacancies_name = 'Python OR Java'
    # vacancies_description = 'DJANGO OR SPRING'
    params = {
        # 'text': 'NAME:(python developer) OR (python developer)',
        # 'text': 'NAME:(Python OR Java) AND (DJANGO OR SPRING)',
        'text': f'NAME:({vacancies_name}) AND ({vacancies_description})',
        # 'text': 'NAME:Django Python Middle+/Senior',
        'area': city_id,
        # Есть страницы т.к. данных много
        # 'page': 1
    }

    result = requests.get(url_vacancies, params=params).json()
    # found = result['found']
    # per_page = result['per_page']
    pages = result['pages']
    # page = result['page']

    normal_break = False  # Завершили обработку по причине отсутствия вакансий

    skills_lst = []  # Список, в котором хранятся встреченные требования.
    # Содержит информацию по всем вакансиям из запроса

    # Можно смотреть количество вакансий в параметре result['found']
    # или смотреть длину списка в параметре len(result['items'])
    if len(result['items']) == 0:
        # Вакансии отсутствуют
        print('Вакансии отсутствуют.')
    else:
        # Вакансии имеются
        normal_break = True  # Завершили обработку, обработав какие-то вакансии
        for page in range(pages):
            # Перебираем все страницы
            if page > 1:
                break  # Так как обработка тестовая, то обрабатываем только первые три страницы: 0, 1, 2.
            print(f'Страница {page + 1} из {pages}')
            params['page'] = page

            # В переменной result лежит список с вакансиями по сокращённой форме
            # Количество определяется параметром per_page в запросе (по умолчанию - 20)
            result = requests.get(url_vacancies, params=params).json()

            count_vacancies += len(result['items'])  # увеличили количество обработанных вакансий
            for vacancy in result['items']:
                # Перебираем вакансии на полученной странице
                skills_set = set()  # Множество, в котором хранятся встреченные требования
                # из параметра key_skills.
                # Содержит информацию по конкретной вакансии из запроса.
                # Используется для того, что бы отсечь двойной подсчет навыков,
                # если они встретятся как в ключевых навыках, так и в описании.

                # считаем заработную плату
                if vacancy['salary'] is None:
                    count_None += 1
                else:
                    # vacancy["salary"]: {'from': 60000,
                    #                     'to': 150000,
                    #                     'currency': 'RUR',
                    #                     'gross': False
                    #                    }
                    currency = vacancy['salary']['currency']
                    count[currency] = count.get(currency, 0) + 1
                    salary_par_num = 0
                    if vacancy['salary']['from'] is None:
                        salary_from = 0
                    else:
                        salary_from = vacancy['salary']['from']
                        salary_par_num += 1
                    if vacancy['salary']['to'] is None:
                        salary_to = 0
                    else:
                        salary_to = vacancy['salary']['to']
                        salary_par_num += 1

                    salary[currency] = (salary.get(currency, 0) +
                                        (salary_from + salary_to) / salary_par_num)

                # Собираем требования
                url_full_vacancy = vacancy['url']
                result_full_vacancy = requests.get(url_full_vacancy).json()

                # Собираем требования из ключевых навыков
                for skill in result_full_vacancy['key_skills']:
                    skills_lst.append(skill['name'].lower())
                    skills_set.add(skill['name'].lower())
                # Определяем навыки из описания
                description = result_full_vacancy['description']
                # Формируем список всех вхождений, удовлетворяющих регулярному выражению
                skills_re = re.findall(r'\s[A-Za-z-?]+-?(?:\s+\d+(?:\.(?:\d+|\*))*)?',
                                       description)
                '''
                Разбор регулярного выражения взят из пояснений выше.
                Итоговое регулярное выражение (проверка онлайн: https://regex101.com/ ):
                \s[A-Za-z-?]+-?(?:\s+\d+(?:\.(?:\d+|\*))*)? 
                  Пояснение:
                  ( https://habr.com/ru/post/349860/?ysclid=l7ymfl4bq8118369293 )
                  - \s — совпадает с пробельными символами (\t, \n, \r, \f и пробелом)
                  - bar+ — соответствует 1 или более вхождениям "bar".
                  - foo* — соответствует 0 или более вхождений "foo".
                  - foo? — соответствует 0 или 1 вхождению "foo".
                  - [4fw] — соответствует любому из символов в скобках.
                  - A-Z - символы от "A" до "Z"
                  - \d - десятичная цифра. Аналог: [0-9]
                  - \. - символ точка (".")
                  - \* - символ звёздочка ("*")
                  - скобки (?:...) позволяют локализовать часть шаблона, внутри которого происходит перечисление.
                    Если  писать круглые скобки и без значков ?:, то от этого у группировки значительно 
                    меняется смысл.
                    Итак, если REGEXP — шаблон, то (?:REGEXP) — эквивалентный ему шаблон. Разница только 
                    в том, что теперь к (?:REGEXP) можно применять квантификаторы, указывая, сколько именно 
                    раз должна повториться группа.
                '''
                # Формируем множество из списка, предварительно убирая концевые пробелы и тире
                # Так же приводим к маленьким буквам.
                skills_description = set(x.strip(' -').lower() for x in skills_re)

                for i in skills_description:
                    if not any(i in x for x in skills_set):
                        # То есть, берём навык из описания и смотрим, чтобы
                        # он не включался в навык из параметра key_skills.
                        # Функция any() возвращает True, если какой-либо (любой)
                        # элемент в итерируемом объекте является истинным True,
                        # в противном случае any() возвращает значение False.
                        skills_lst.append(i)

    result_json = {}
    result_data = ''
    if normal_break:
        # Вакансии были обработаны
        # collections.Counter() - функция принимает итерируемый аргумент и
        # возвращает словарь, в котором ключами служат индивидуальные элементы,
        # а значениями – количества повторений элемента в переданной последовательности.
        counted_skills = Counter(skills_lst)
        # result_json = {}
        print('Тестовые переменные:')
        print('count', count)
        print('salary', salary)
        print('требуемые навыки (весь список)', counted_skills)
        print()
        print('Итоговый вывод:')
        print('Всего обработано вакансий:', count_vacancies)
        result_data = f'Всего обработано вакансий: {count_vacancies}\n'
        result_json['count_vacancies'] = count_vacancies
        print('вакансий с отсутствующей зарплатой:', count_None)
        result_data += f'Вакансий с отсутствующей зарплатой: {count_None}\n'
        result_json['count_None_salary'] = count_None
        print()
        print('Средняя зарплата в разных валютах:')
        result_data += f'\nСредняя зарплата в разных валютах:\n'
        result_json['salary'] = {}
        if len(count.keys()) > 0:
            for currency in count.keys():
                print(f'    Средняя зарплата в валюте {currency}: {round(salary[currency] / count[currency], 2)}.')
                result_data += f'    Средняя зарплата в валюте {currency}: {round(salary[currency] / count[currency], 2)}.\n'
                result_json['salary'].update({f'{currency}': round(salary[currency] / count[currency], 2)})
                # result_json[f'{currency}_salary'] = round(salary[currency]/count[currency], 2)

        requirements = []  # Тут итоговые данные по требованиям
        result_data += '\nНавыки (первые 5)\n'
        for name, requirements_count in counted_skills.most_common(5):
            # Метод most_common(n) ищет n самых повторяющихся элементов.
            print(f'Навык: {name}.',
                  f'Указан: {requirements_count} раза.',
                  f'Частота: {round((requirements_count / count_vacancies) * 100, 2)}.')
            result_data += (f'Навык: {name}.' +
                            f'Указан: {requirements_count} раза.' +
                            f'Частота: {round((requirements_count / count_vacancies) * 100, 2)}.\n')

            requirements.append({'name': name,
                                 'count': requirements_count,
                                 'percent': round((requirements_count / count_vacancies) * 100, 2)})
            result_json['requirements'] = requirements

        print('===============')
        pprint.pprint(result_json)
        print(result_data)
        # сохранение файла с результатами работы
        with open('result_data.txt', mode='w') as f:
            f.write(result_data)
        with open('result_data.json', mode='w') as f:
            json.dump(result_json, f)

    else:
        # Вакансий при обработке запроса не было
        print('Вакансий при обработке запроса не было')
    # pprint.pprint(result[0]['areas'])
    # pprint.pprint(result)
    # Возврат: result_json - словарь, result_data - строка
    #     result_json = {'count_None_salary': 31,
    #                    'count_vacancies': 40,
    #                    'requirements': [{'count': 26, 'name': 'java', 'percent': 65.0},
    #                                     {'count': 20, 'name': 'sql', 'percent': 50.0},
    #                                     {'count': 20, 'name': 'git', 'percent': 50.0},
    #                                     {'count': 19, 'name': 'postgresql', 'percent': 47.5},
    #                                     {'count': 18, 'name': 'docker', 'percent': 45.0}],
    #                    'salary': {'RUR': 216676.67}}
    #     result_data = '''
    #                     Всего обработано вакансий: 40
    #                     Вакансий с отсутствующей зарплатой: 31
    #
    #                     Средняя зарплата в разных валютах:
    #                         Средняя зарплата в валюте RUR: 216676.67.
    #
    #                     Навыки (первые 5)
    #                     Навык: java.Указан: 26 раза.Частота: 65.0.
    #                     Навык: sql.Указан: 20 раза.Частота: 50.0.
    #                     Навык: git.Указан: 20 раза.Частота: 50.0.
    #                     Навык: postgresql.Указан: 19 раза.Частота: 47.5.
    #                     Навык: docker.Указан: 18 раза.Частота: 45.0.
    #                   '''
    return result_json, result_data


if __name__ == '__main__':
    # city_name = 'Москва'  # Тут должен стоять ввод через input:
    # # city_name = input('Введите город для поиска вакансий')
    # vacancies_name = 'Python OR Java'  # Тут должен стоять ввод через input
    # vacancies_description = 'DJANGO OR SPRING'  # Тут должен стоять ввод через input
    searching_vacancies(city_name='Москва',
                        vacancies_name='Python OR Java',
                        vacancies_description='DJANGO OR SPRING',
                        domain='https://api.hh.ru/')
