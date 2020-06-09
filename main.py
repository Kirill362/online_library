import requests
from bs4 import BeautifulSoup
import os
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import json
import argparse

def download_txt(url, filename, folder='books/'):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    with open("{}/{}.txt".format(folder, filename), "w", encoding="utf-8") as my_file:
        my_file.write(response.text)
    return os.path.join('folder', 'filename')


def download_image(url, filename, folder='images/'):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    with open("{}/{}".format(folder, filename), "wb") as my_file:
        my_file.write(response.content)
    return os.path.join('folder', 'filename')


def create_book_information(code, link):
    soup = BeautifulSoup(code, 'lxml')
    book_information = find_title_and_author(soup)
    book_information["img_src"], book_information["comments"] = find_img_and_comments(soup, link)
    book_information["genres"] = find_genres(soup)
    return book_information


def find_title_and_author(soup):
    title_tag = soup.select_one('div h1')
    title, author = title_tag.text.split("   ::   ")
    title = sanitize_filename(title)
    book_information = {"title": title,
                        "author": author}
    return book_information


def find_img_and_comments(soup, link):
    picture_tag = soup.select_one('div.bookimage a img')['src']
    full_image_url = urljoin(link, picture_tag)

    comment_tag = soup.select('div.texts')
    if comment_tag == []:
        comments = ["Комментариев пока нет"]
    else:
        comments = []
        for comment in comment_tag:
            comments.append(comment.find('span').text)
    return full_image_url, comments


def find_genres(soup):
    genres =[]
    genre_tag = soup.select('span.d_book a')
    for tag in genre_tag:
        genres.append(tag.text)
    return genres


def find_last_page():
    url = "http://tululu.org/l55/"
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    print(soup.select("p.center a.npage"))
    last_page = int(soup.select("p.center a.npage")[-1].text) + 1
    return last_page


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Скачивание книг с определённых страниц')
    parser.add_argument('--start_page', help='С какой страницы начать скачивание', default=701, type=int)
    parser.add_argument('--end_page', help='На какой странице закончить скачивание', default=find_last_page(), type=int)
    parser.add_argument('--dest_folder', help='Путь к каталогу с результатами парсинга: картинкам, книгами, JSON', default='')
    parser.add_argument('--skip_imgs', help='Hе скачивать картинки', default=False, action='store_true')
    parser.add_argument('--skip_txt', help='Hе скачивать книги', default=False, action='store_true')
    parser.add_argument('--json_path', help='Указать свой путь к *.json файлу с результатами', default='')
    args = parser.parse_args()

    books_list = []

    for page_id in range(args.start_page, args.end_page):
        fantasy_books_url = "http://tululu.org/l55/{}/".format(page_id)
        response = requests.get(fantasy_books_url, allow_redirects=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        link_tags = soup.select("table.d_book")
        for tag in link_tags:
            book_url = tag.select_one("a")["href"]
            full_book_url = urljoin(fantasy_books_url, book_url)
            response = requests.get(full_book_url, allow_redirects=False)
            response.raise_for_status()
            if response.status_code == 200:
                book_information = create_book_information(response.text, full_book_url)
                filename = book_information["img_src"].split("/")[-1]
                if not args.skip_imgs:
                    download_image(book_information["img_src"], filename, "{}images/".format(args.dest_folder))
                download_book_url = 'http://tululu.org/txt.php?id={}'.format(book_url[2:-1])
                if not args.skip_txt:
                    download_txt(download_book_url, book_information["title"], "{}books/".format(args.dest_folder))
                books_list.append(book_information)

    os.makedirs("{}{}".format(args.dest_folder, args.json_path), exist_ok=True)

    with open("{}{}books_info.json".format(args.dest_folder, args.json_path), "w") as my_file:
        json.dump(books_list, my_file)
