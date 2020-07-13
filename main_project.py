import random
import bs4
import pandas as pd
import convert
import requests


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
filtered = dat[dat['count'] >= 3]

# создаем множество уникальных чтений
unique = set(filtered.loc[:, 'reading'])

# выбираем из множества один элемент (и удаляем его)
reading = unique.pop()
print(reading, convert.romajiToJapanese(reading))

# отбираем строки из датасета только с выбранным чтением
choice = filtered[filtered['reading'] == reading]

# создаем список из иероглифов с этим чтением
writings = list(choice.loc[:, 'writing'])

# конвертируем чтение с ромадзи в хирагану
reading = convert.romajiToJapanese(reading)

# если нашлось больше 4 иероглифов, отбираем 4
if len(writings) > 4:
    writings = random.choices(writings, k=4)

print('иероглифы :', writings)

components = []
for writing in writings:
    # конструктор поискового запроса
    url = 'https://www.kanshudo.com/searchq?q=' + writing + ':' + reading
    # парсим страницу
    url = requests.get(url)
    soup = bs4.BeautifulSoup(url.content, 'html.parser')

    # создаем список слов с данным иероглифом с заданным чтением
    words = soup.find_all(class_="f_container")
    # выбираем слово, пока что случайным образом
    while True:
        word = random.choice(words)
        hiragana = list(word.children)[0].get_text()
        kanji = list(word.children)[1].get_text()
        # проверяем, что слово составное
        if len(kanji) > 1:
            break

    # создаем ребус, заменяя в словах иеролгифы с одинаковыми чтениями на пробелы
    puzzle = kanji.replace(writing, '|__|')

    # сохраняем элементы ребуса в список
    components.append(dict([('hiragana', hiragana), ('kanji', kanji), ('puzzle', puzzle)]))
    # print(hiragana, kanji, puzzle)

print('Ребус')
print(reading)
for component in components:
    print(component['puzzle'])
print()
print('Подсказка')
for component in components:
    print(f"{component['puzzle']} читается как {component['hiragana']}")
print()
print('Ответ')
for component in components:
    print(f"{component['puzzle']} читается как {component['hiragana']} и пишется как {component['kanji']}")


