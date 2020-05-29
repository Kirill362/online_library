import requests
from bs4 import BeautifulSoup
import os
from pathvalidate import sanitize_filename
from urllib.parse import urljoin

def download_txt(url, filename, folder='books/'):
    if not os.path.exists(folder):
        os.makedirs(folder)
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    sanitized_filename = sanitize_filename(filename)
    if response.status_code == 200:
        with open("{}/{}.txt".format(folder, sanitized_filename), "w") as my_file:
            my_file.write(response.text)
    return os.path.join('folder', 'filename')

def download_image(url, filename, folder='images/'):
    if not os.path.exists(folder):
        os.makedirs(folder)
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    with open("{}/{}".format(folder, filename), "wb") as my_file:
        my_file.write(response.content)
    return os.path.join('folder', 'filename')

genres = []
for book_id in range(1, 11):
    site_url = 'http://tululu.org/b{}/'.format(book_id)
    response = requests.get(site_url, allow_redirects=False)
    response.raise_for_status()
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        title_tag = soup.find('div', id='content').find('h1')
        title_and_author = title_tag.text.split("   ::   ")
        title = "{}. {}".format(book_id, title_and_author[0])
        print(title)
        author = title_and_author[1]

        picture_tag = soup.find('div', class_="bookimage").find('a').find('img')['src']
        full_image_url = urljoin(site_url, picture_tag)
        filename = full_image_url.split("/")[-1]
        comment_tag = soup.find_all('div', class_='texts')
        #if comment_tag == []:
            #print("Комментариев пока нет")
        #else:
            #for comment in comment_tag:
                #print(comment.find('span').text)

        genre_tag = soup.find('span', class_='d_book').find_all('a')
        for tag in genre_tag:
            genres.append(tag.text)
        print(genres)
        genres = []
    #download_image(full_image_url, filename)
    #book_url = 'http://tululu.org/txt.php?id={}'.format(book_id)
    #download_txt(book_url, title)




