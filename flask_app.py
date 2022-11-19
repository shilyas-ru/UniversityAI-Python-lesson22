import pprint

from flask import Flask, render_template, request, Markup

from lesson18_main import searching_vacancies

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/hhparser/index.html')
@app.route('/hhparser/')
def hhparser_index():
    return render_template('hhparser/index.html')


@app.route('/hhparser/form.html')
def hhparser_search():
    return render_template('/hhparser/form.html')


# Вариант:
# @app.post('/hhparser/about.html')
@app.route('/hhparser/about.html', methods=['POST'])
def hhparser_result():
    template_data = {'query': request.form.get('query'),
                     'where': request.form.get('where')}
    # Если render_template() нужно передать много аргументов,
    # можно не разделять их запятыми (,), а создать словарь и
    # использовать оператор **, чтобы передать аргументы-ключевые
    # слова функции. Например:
    # @app.route('/')
    # def index():
    #     name, age, profession = "Jerry", 24, 'Programmer'
    #     template_context = dict(name=name_data,
    #                             age=age_data,
    #                             profession=profession_data)
    #     return render_template('index.html', **template_context)
    # Шаблон index.html теперь имеет доступ к трем переменным
    # шаблона: name, age и profession
    vacancies_name = ''
    vacancies_description = ''
    if template_data['where'] == 'all':  # Ищем 'Везде'
        template_data['where'] = 'Везде'
        vacancies_name = template_data['query']
        vacancies_description = template_data['query']
    elif template_data['where'] == 'vacancies_name':  # Ищем 'В названии вакансии'
        template_data['where'] = 'В названии вакансии'
        vacancies_name = template_data['query']
    else:  # Ищем 'В описании вакансии'
        template_data['where'] = 'В описании вакансии'
        vacancies_description = template_data['query']

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

    #
    # Получить данные из словаря
    #     result_json = {...
    #                    'requirements': [{'count': 26,
    #                                      'name': 'java',
    #                                      'percent': 65.0},
    #                                     ...
    #                                     }],
    #                    ...
    #
    # можно разными способами:
    #  - result_json.requirements[0].count: 26
    #  - result_json['requirements'][0]['count']: 26
    # подробнее в документации:
    # https://jinja.palletsprojects.com/en/2.10.x/templates/#synopsis
    result_json, result_data = searching_vacancies(city_name='',   # 'Москва',
                                                   vacancies_name=vacancies_name,
                                                   vacancies_description=vacancies_description,
                                                   domain='https://api.hh.ru/')
    result_data = result_data.replace('\n', '<br>')
    # источник: https://flask-russian-docs.readthedocs.io/ru/latest/templating.html
    # Управление автоэкранированием
    # Автоэкранирование - это автоматическое экранирование специальных символов.
    # Специальными символами в HTML (а также в XML и в XHTML) являются &, >, <, " и '.
    # Поскольку эти символы имеют особое значение в документах, для использования в
    # тексте их нужно заменить на так называемые «сущности». Если этого не сделать,
    # это не только может повлиять на невозможность использования этих символов
    # пользователем, но и привести к проблемам с безопасностью (см. xss).
    #
    # Однако, иногда в шаблонах может потребоваться отключить автоэкранирование.
    # Это может понадобиться, если нужно явным образом вставить в страницу фрагмент HTML,
    # если фрагмент поступил из системы генерации безопасного HTML, например, из
    # преобразователя markdown в HTML.
    #
    # Для достижения этого есть три способа:
    #
    #   - В коде Python обернуть строку HTML в объект Markup перед передачей в шаблон.
    #     Это рекомендуемый способ.
    #   - Внутри шаблона, воспользовавшись фильтром |safe для явной отметки строки,
    #     как безопасного HTML ({{ myvariable | safe }})
    #   - Временно отключить систему автоэкранирования.
    #
    # Для отключения системы автоэкранирования в шаблонах можно воспользоваться
    # блоком {% autoescape %}:
    #
    # {% autoescape false %}
    #     <p>autoescaping is disabled here
    #     <p>{{ will_not_be_escaped }}
    # {% endautoescape %}
    #
    # Соблюдайте осторожность и всегда следите за переменными,
    # которые помещаете в этот блок.
    #
    #
    # Источник: https://flask-russian-docs.readthedocs.io/ru/0.10.1/quickstart.html#id7
    # Автоматическая обработка специальных (escape-) последовательностей (escaping)
    # включена по умолчанию, поэтому если name содержит HTML, он будет экранирован
    # автоматически. Если вы можете доверять переменной и знаете, что в ней будет
    # безопасный HTML (например, потому что он пришёл из модуля конвертирования
    # разметки wiki в HTML), вы можете пометить её в шаблоне, как безопасную - с
    # использованием класса Markup или фильтра |safe. За дополнительными примерами
    # обратитесь к документации по Jinja2.
    # >>> from flask import Markup
    # >>> Markup('<strong>Hello %s!</strong>') % '<blink>hacker</blink>'
    #       Markup(u'<strong>Hello &lt;blink&gt;hacker&lt;/blink&gt;!</strong>')
    # >>> Markup.escape('<blink>hacker</blink>')
    #       Markup(u'&lt;blink&gt;hacker&lt;/blink&gt;')
    # >>> Markup('<em>Marked up</em> &raquo; HTML').striptags()
    #       u'Marked up \xbb HTML'
    template_data.update({'result_json': result_json,
                          'result_data': Markup(result_data)})
    return render_template('/hhparser/about.html', **template_data)


@app.route('/bootstrap4/test_bs4.html')
def bootstrap4_test_bs4():
    return render_template('/bootstrap4/test_bs4.html')


# Можно сделать так:
# @app.route('/bootstrap5/test_carousel.html', methods=['GET', 'POST'])
# def bootstrap5_test_carousel():
#     if request.method == 'POST':
#         pass
#     else:
#         pass
#     return render_template('/bootstrap5/test_carousel.html')

# А можно разнести по двум разным методам: @app.get и @app.post
@app.get('/bootstrap5/test_carousel.html')
def bootstrap5_test_carousel_get():
    return render_template('/bootstrap5/test_carousel.html')


@app.post('/bootstrap5/test_carousel.html')
def bootstrap5_test_carousel_post():
    return render_template('/bootstrap5/test_carousel.html')


if __name__ == "__main__":
    app.run(debug=True)
