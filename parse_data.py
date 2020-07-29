import requests
from bs4 import BeautifulSoup

page = requests.get('https://en.wikipedia.org/wiki/Ky%C5%8Diku_kanji')
soup = BeautifulSoup(page.content, 'html.parser')


