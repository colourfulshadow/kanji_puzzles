import random
import bs4
import pandas as pd
import convert  # спасибо https://github.com/aleckretch/Romaji-to-Japanese-Converter
import requests

M = 3  # минимальное количество слов в ребусе
N = 4  # предпочтительное количество слов в ребусе


# читаем файл эксель
def read_excel(filename):
    df = pd.ExcelFile(filename).parse()
    df.fillna(method='ffill', inplace=True)
    return df


# приводим считанный датафрейм к удобному для работы с ним формату
def transform_dataframe(df):
    df.loc[:, 'reading'] = df['on']
    df.loc[:, 'writing'] = df['kanji']

    # задаем с клавиатуры уровень или выставляем максимальный (6) по умолчанию
    max_grade = input('Выберите максималный уровень (1-6) или любой символ:')
    try:
        max_grade = int(max_grade)
        if not 0 < max_grade < 7:
            max_grade = 6
    except ValueError:
        max_grade = 6

    # при необходимости обрезаем датасет
    if max_grade < 6:
        df = df.loc[df['grade'] <= max_grade].copy()

    # добавляем столбец с частотностью чтений в датасете
    df.loc[:, 'count'] = df.groupby('on').transform('count').loc[:, 'reading']
    df.set_index(['kanji', 'on'], inplace=True)

    # оставляем строки только с теми чтениями, частотность которых удовлетворяет минимальному значеню
    df = df.loc[df['count'] >= M].copy()
    return df


def choose_reading_and_writings(filtered):
    # отбираем в датасет чтения, соответствующие условию
    # filtered = df[df['count'] >= M]

    # создаем множество уникальных чтений
    unique = set(filtered.loc[:, 'reading'])

    # задаем чтение с клавиатуры
    reading = input('Введите чтение или любой символ: ')
    if reading not in unique:
        print('С этим чтением нельзя сделать ребус. Выберем другое.')

        # или выбираем чтение из множества (и удаляем его)
        reading = unique.pop()
    print(reading, convert.romajiToJapanese(reading))

    # отбираем строки из датасета только с выбранным чтением
    choice = filtered[filtered['reading'] == reading]

    # создаем список из иероглифов с этим чтением
    writings = list(choice.loc[:, 'writing'])

    # конвертируем чтение с ромадзи в хирагану
    reading = convert.romajiToJapanese(reading)

    print('иероглифы :', writings)
    return reading, writings


def create_puzzle(reading, writings):
    word_cards = []
    for writing in writings:

        # создаем конструктор поискового запроса
        url = 'https://www.kanshudo.com/searchq?q=' + writing + ':' + reading
        # парсим страницу
        url = requests.get(url)
        soup = bs4.BeautifulSoup(url.content, 'html.parser')

        # создаем список словарных карточек с данным иероглифом с заданным чтением
        elements = soup.find_all(class_="jukugorow first last")
        level = 1
        index = 1

        # определяем самый легкий доступный уровень jlpt
        for element in elements:
            jlpt = element.find(class_="w_ref")
            if jlpt is not None and int(jlpt.get_text()) > level:
                level = int(jlpt.get_text())
                index = elements.index(element)

        # парсим словарную карточку по полученному индексу
        element = elements[index]
        word = element.find(class_='f_container')
        jlpt = element.find(class_="w_ref")
        if jlpt is not None:
            jlpt = int(jlpt.get_text())
        # meaning = element.find_all(class_="vm")
        # print(len(meaning), meaning[0].get_text(), meaning)

        hiragana = list(word.children)[0].get_text()
        kanji = list(word.children)[1].get_text()

        # придумать, как запустить это в цикл, чтобы он искал следующее слово!
        if len(kanji) > 1:
            # создаем ребус, заменяя в словах иеролгифы с одинаковыми чтениями на пробелы
            puzzle = kanji.replace(writing, '_')

            # сохраняем элементы ребуса в список словарей
            word_cards.append(dict(
                [('hiragana', hiragana), ('kanji', kanji), ('puzzle', puzzle), ('jlpt', jlpt), ('reading', reading)]))

    if len(word_cards) > N:
        for_printing = []
        for i in range(5, 0, -1):
            for word_card in word_cards:
                if word_card['jlpt'] == i:
                    for_printing.append(word_card)
        for word_card in word_cards:
            if word_card['jlpt'] is None:
                for_printing.append(word_card)

        word_cards = for_printing
    return word_cards


def printing(word_cards):
    print('Ребус')
    print(word_cards[0]['reading'])
    for word_card in word_cards[:N]:
        print(f"{word_card['puzzle']} (N{word_card['jlpt']})")
    print()
    print('Подсказка 1')
    for word_card in word_cards[:N]:
        print(f"{word_card['puzzle']} читается как {word_card['hiragana']}")
    # print()
    # print('Подсказка 2')
    # for component in components:
    #     print(f"{component['puzzle']} на английском будет {component['meaning']}")
    print()
    print('Ответ')
    for word_card in word_cards[:N]:
        print(f"{word_card['puzzle']} пишется как {word_card['kanji']} и читается как {word_card['hiragana']} ")

# printing(create_puzzle(*choose_reading_and_writings(choose_sheet())))
