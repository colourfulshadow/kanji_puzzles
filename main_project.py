import random
import bs4
import pandas as pd
import convert  # спасибо https://github.com/aleckretch/Romaji-to-Japanese-Converter
import requests

M = 3  # минимальное количество слов в ребусе
N = 4  # предпочтительное количество слов в ребусе


# читаем лист из экселя
def read_sheet(filename, level):
    xl = pd.ExcelFile(filename)
    df = xl.parse(xl.sheet_names[level - 1])
    df.fillna(method='ffill', inplace=True)
    df['reading'] = df['on']
    df['writing'] = df['kanji']
    df['count'] = df.groupby('on').transform('count').loc[:, 'reading']

    df.set_index(['kanji', 'on'], inplace=True)
    return df


# задаем максимальный уровень
max_grade = int(input('Enter max grade: '))

# читаем соответствующий лист в датафрейм
dat = read_sheet('kanji_database1.xlsx', max_grade)

# отбираем в датасет чтения, встречающиеся более трех раз
filtered = dat[dat['count'] >= M]

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

# если нашлось больше 4 иероглифов, случайным образом отбираем 4
# if len(writings) > 4:
#     writings = random.sample(writings, k=4)

print('иероглифы :', writings)

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
        puzzle = kanji.replace(writing, '|__|')

        # сохраняем элементы ребуса в список словарей
        word_cards.append(dict([('hiragana', hiragana), ('kanji', kanji), ('puzzle', puzzle), ('jlpt', jlpt)]))

if len(word_cards) > N:
    for_printing = []
    for i in range(5, 0, -1):
        for word_card in word_cards:
            if word_card['jlpt'] == i:
                for_printing.append(word_card)
    for word_card in word_cards:
        if word_card['jlpt'] is None:
            for_printing.append(word_card)

    print(for_printing)
    word_cards = for_printing

print('Ребус')
print(reading)
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
