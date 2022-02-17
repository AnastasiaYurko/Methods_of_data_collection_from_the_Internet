from pprint import pprint

from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
from pymongo.errors import *

client = MongoClient('localhost', 27017)
db = client['hh_ru']
collection = db.vacancies

# https://spb.hh.ru/search/vacancy?area=2&fromSearchLine=true&text=python
url = 'https://spb.hh.ru'
params = {'area': 2,
          'fromSearchLine': 'true',
          'text': 'python'}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}

response = requests.get(url + '/search/vacancy', params=params, headers=headers)

while response is not None:

    soup = BeautifulSoup(response.text, 'html.parser')

    vacancies = soup.find_all('div', {'class': 'vacancy-serp-item'})

    for vacancy in vacancies:
        vacancy_data = {}
        info = vacancy.find('span', {'class': 'resume-search-item__name'})
        name = info.text
        link = info.find('a').get('href')
        link_list = link.split('/')
        vacancy_id_list = link_list[-1].split('?')
        vacancy_id = vacancy_id_list[0]
        try:
            salary = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}).text
            salary_list = salary.split()
        except:
            salary = None
            min_sal = None
            max_sal = None
            currency = None

        if salary is not None:
            if salary_list[0] == 'от':
                min_sal = int(salary_list[1]) * 1000
                max_sal = None
                currency = salary_list[3]
            elif salary_list[0] == 'до':
                min_sal = None
                max_sal = int(salary_list[1]) * 1000
                currency = salary_list[3]
            else:
                min_sal = int(salary_list[0]) * 1000
                max_sal = int(salary_list[3]) * 1000
                currency = salary_list[5]

        vacancy_data['_id'] = vacancy_id
        vacancy_data['name'] = name
        vacancy_data['link'] = link
        vacancy_data['min salary'] = min_sal
        vacancy_data['max salary'] = max_sal
        vacancy_data['currency'] = currency
        vacancy_data['site'] = url

        try:
            db.collection.insert_one(vacancy_data)
        except DuplicateKeyError:
            print('Данная вакансия уже существует')

    try:
        next_page = soup.find('a', {'data-qa': 'pager-next'}).get('href')

        response = requests.get(url + next_page, headers=headers)
    except:
        response = None

for vacancy in db.collection.find({'min salary': {'$gt': 30000}, 'max salary': {'$gt': 50000}}):
    pprint(vacancy)
