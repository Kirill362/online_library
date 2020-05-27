import requests
from bs4 import BeautifulSoup
import os
from pathvalidate import sanitize_filename

def download_txt(url, filename, folder='books/'):
    if not os.path.exists(folder):
        os.makedirs(folder)
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    sanitized_filename = sanitize_filename(filename)
    if response.status_code == 200:
        with open("{}/{}.txt".format(folder, sanitized_filename), "w") as my_file:
            my_file.write(response.text)


for book_id in range(1, 11):
    site_url = 'http://tululu.org/b{}/'.format(book_id)
    response = requests.get(site_url, allow_redirects=False)
    response.raise_for_status()
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        title_tag = soup.find('div', id='content').find('h1')
        title_and_author = title_tag.text.split("   ::   ")
        title = "{}. {}".format(book_id, title_and_author[0])
        author = title_and_author[1]
    book_url = 'http://tululu.org/txt.php?id={}'.format(book_id)
    download_txt(book_url, title)



