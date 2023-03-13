# Patrycjusz Bachleda
# SOFTWARE ENGINEERING I (CS_361_400_S2022)
# Microservice to extract data from Wikipedia

import time
import requests
from bs4 import BeautifulSoup


def request():
    """checks if there is a request"""
    file = open('request.txt', 'r')
    searchWord = file.readline()
    file.close()
    return searchWord.replace(' ', '_')  # creates a valid name


def get_from_Wikipedia():
    """requests data from Wikipedia"""
    link = "https://en.wikipedia.org/wiki/" + searchWord
    print(link)
    result = requests.get(link)
    print(result.status_code, '\n')
    all_page_info = result.content  # stores the content of the page as a variable
    return BeautifulSoup(all_page_info,
                         'lxml')  # creates BeautifulSoup object based on the all_page_info variable to parse and process the info


def table():
    """extracts data from the table"""
    for tr_tag in soup.find_all('tr'):
        table = tr_tag.text
        if table[0:8] == 'Vertical':
            # some pages have no spaces between words and numbers in the table
            table = table[0:8] + ' ' + table[8:]
            data.append(table)
        elif table[0:3] == 'Top':
            table = table[0:13] + ' ' + table[13:]
            data.append(table)
        elif table[0:4] == 'Base':
            table = table[0:14] + ' ' + table[14:]
            data.append(table)
        elif table[0:7] == 'Skiable':
            table = table[0:12] + ' ' + table[12:]
            data.append(table)
            break


def text():
    """extracts paragraphs"""
    num_paragraphs = 10  # the number of saved paragraphs can be changed
    for p_tags in soup.find_all('p'):
        paragraph = p_tags.text
        if len(paragraph) > 2 and num_paragraphs > 0:  # skips empty paragraphs if len(paragraph) > 2
            num_paragraphs -= 1
            data.append(paragraph)
        if num_paragraphs <= 0:
            break


def response():
    """saves extracted data into the file"""
    file = open('response.txt', encoding='utf-8', mode='w')
    for i in data:
        # removes unnecessary signs and extra spaces from the text
        i = i.replace('\xa0', ' ')
        i = i.replace('   ', ' ')
        i = i.replace('  ', ' ')
        i = i.replace('\n', '')
        file.write(i + '\n')
    file.close()


wait = ''  # a variable used when checking if a new request received

while True:  # it runs constantly and checks if a new request received
    searchWord = request()
    #time.sleep(1)  # the delay is needed to give time for the application to write the request in the file
    if searchWord != wait:  # only if a new request received
        wait = searchWord
        print('new request received')
        soup = get_from_Wikipedia()
        data = [searchWord + ':']  # to store the extracted data
        table()
        text()
        response()
