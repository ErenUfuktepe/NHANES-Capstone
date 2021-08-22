import requests
from bs4 import BeautifulSoup
import re
import os


def extract_from_table(content, new_response):
    new_soup = BeautifulSoup(new_response.text, features='html.parser')
    tbody = new_soup.find_all('tbody')
    tr = tbody[0].find_all('tr')
    my_dictionary_list = list(map(lambda x: get_folder_and_file_name(x), tr))
    print('\nDownloading ', content, '- Number of Elements : ', len(my_dictionary_list))
    list(map(lambda x: download(content, x['Name'], x['Href']) if x is not None else '', my_dictionary_list))


def get_folder_and_file_name(new_tr):
    try:
        td = new_tr.find_all('td')
        name = (list(td[0].children)[0])
        href = td[2].a['href']
        return {'Name': name, 'Href': href}
    except:
        return None


def download(content, folder, url):
    global download_url, BASE_DIR, year
    filename = url.split('/')[-1]
    folder = folder.replace(":", "")
    path = os.path.join(BASE_DIR, "data/{year}/{content}/{folder}".format(year=year, content=content, folder=folder))
    if not os.path.exists(path):
        os.makedirs(path)
    os.chdir(path)
    new_request = requests.get(download_url.format(href=url), allow_redirects=True)
    open(filename, 'wb').write(new_request.content)
    print('Folder : ', folder, '- File : ', filename)


BASE_DIR = os.getcwd()
main = 'https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?BeginYear={year}'
data_url = 'https://wwwn.cdc.gov/nchs/nhanes/search/datapage.aspx?Component={component}&CycleBeginYear={year}'
download_url = 'https://wwwn.cdc.gov/{href}'

year = 2017

response = requests.get(main.format(year=year), allow_redirects=True)
soup = BeautifulSoup(response.text, features='html.parser')

div = soup.find_all('div', class_='card mb-3')
div_data = div[0].find_all('a')
data = list(map(lambda x: re.sub('\s+', '', list(x.children)[-1]).replace("Data", ""), div_data))

list(map(lambda x: extract_from_table(x, requests.get(data_url.format(component=x, year=year), allow_redirects=True)),
         data))
