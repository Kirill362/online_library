import requests
from bs4 import BeautifulSoup
import os
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import json
import argparse

def download_txt(url, filename, folder='books/'):
    if not os.path.exists(folder):
        os.makedirs(folder)
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    with open("{}/{}.txt".format(folder, filename), "w", encoding="utf-8") as my_file:
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


parser = argparse.ArgumentParser(
    description='Скачивание книг с определённых страниц'
)
parser.add_argument('--start_page', help='С какой страницы начать скачивание', default=1, type=int)
parser.add_argument('--end_page', help='На какой странице закончить скачивание', default=702, type=int)
parser.add_argument('--dest_folder', help='Путь к каталогу с результатами парсинга: картинкам, книгами, JSON', default='')
parser.add_argument('--skip_imgs', help='Hе скачивать картинки', default=False, action='store_true')
parser.add_argument('--skip_txt', help='Hе скачивать книги', default=False, action='store_true')
parser.add_argument('--json_path', help='Указать свой путь к *.json файлу с результатами', default='')
args = parser.parse_args()

genres = []
books_list = []


for page_id in range(args.start_page, args.end_page):
    fantasy_books_url = "http://tululu.org/l55/{}/".format(page_id)
    response = requests.get(fantasy_books_url, allow_redirects=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    link_tags = soup.select("table.d_book")
    for tag in link_tags:
        url = tag.select_one("a")["href"]
        link = urljoin(fantasy_books_url, url)
        response = requests.get(link, allow_redirects=False)
        response.raise_for_status()
        if response.status_code == 200:
            book_information = {}
            soup = BeautifulSoup(response.text, 'lxml')
            title_tag = soup.select_one('div h1')
            title, author = title_tag.text.split("   ::   ")
            title = sanitize_filename(title)
            book_information["title"] = title
            book_information["author"] = author

            picture_tag = soup.select_one('div.bookimage a img')['src']
            full_image_url = urljoin(link, picture_tag)
            book_information["img_src"] = full_image_url

            filename = full_image_url.split("/")[-1]
            comment_tag = soup.select('div.texts')
            if comment_tag == []:
                comments = ["Комментариев пока нет"]
            else:
                comments = []
                for comment in comment_tag:
                    comments.append(comment.find('span').text)
            book_information["comments"] = comments

            genre_tag = soup.select('span.d_book a')
            for tag in genre_tag:
                genres.append(tag.text)
            book_information["genres"] = genres
            genres = []
            if not args.skip_imgs:
                download_image(full_image_url, filename, "{}images/".format(args.dest_folder))
            book_url = 'http://tululu.org/txt.php?id={}'.format(url[2:-1])
            if not args.skip_txt:
                download_txt(book_url, title, "{}books/".format(args.dest_folder))
            books_list.append(book_information)

if not os.path.exists("{}{}".format(args.dest_folder, args.json_path)):
    os.makedirs("{}{}".format(args.dest_folder, args.json_path))

with open("{}{}books_info.json".format(args.dest_folder, args.json_path), "w") as my_file:
    json.dump(books_list, my_file)







