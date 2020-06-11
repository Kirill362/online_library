import requests
from bs4 import BeautifulSoup
import os
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import json
import argparse
import logging


def download_file(url, path):
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    if 'images' in path:
        with open(path, "wb") as my_file:
            my_file.write(response.content)
    elif 'books' in path:
        with open(path, "w", encoding="utf-8") as my_file:
            my_file.write(response.text)


def create_book_information(code, link):
    soup = BeautifulSoup(code, 'lxml')
    book_information = find_title(soup)
    book_information["author"] = find_author(soup)
    book_information["img_src"] = find_img(soup, link)
    book_information["comments"] = find_comments(soup)
    book_information["genres"] = find_genres(soup)
    return book_information


def find_title(soup):
    title_tag = soup.select_one('div h1')
    title = title_tag.text.split("   ::   ")[0]
    book_information = {"title": title}
    return book_information


def find_author(soup):
    title_tag = soup.select_one('div h1')
    author = title_tag.text.split("   ::   ")[1]
    return author


def find_img(soup, link):
    picture_tag = soup.select_one('div.bookimage a img')['src']
    full_image_url = urljoin(link, picture_tag)
    return full_image_url


def find_comments(soup):
    comment_tags = soup.select('div.texts')
    comments = []
    if comment_tags != []:
        comments = [comment.find('span').text for comment in comment_tags]
    return comments


def find_genres(soup):
    genre_tags = soup.select('span.d_book a')
    genres = [tag.text for tag in genre_tags]
    return genres


def find_last_page():
    url = "http://tululu.org/l55/"
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    try:
        check_redirect(response)
    except requests.exceptions.HTTPError as error:
        logging.warning(f"Обнаружен редирект по ссылке {url}, за последнюю страницу взято стандартное значение (702)")
        return 702
    soup = BeautifulSoup(response.text, 'lxml')
    last_page = int(soup.select("p.center a.npage")[-1].text) + 1
    return last_page


def check_redirect(response):
    if response.is_redirect:
        raise requests.HTTPError(f"Найдена переадрессация {response.url}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Скачивание книг с определённых страниц')
    parser.add_argument('--start_page', help='С какой страницы начать скачивание', default=1, type=int)
    parser.add_argument('--end_page', help='На какой странице закончить скачивание', default=find_last_page(), type=int)
    parser.add_argument('--dest_folder', help='Путь к каталогу с результатами парсинга: картинкам, книгами, JSON', default='./')
    parser.add_argument('--skip_imgs', help='Hе скачивать картинки', default=False, action='store_true')
    parser.add_argument('--skip_txt', help='Hе скачивать книги', default=False, action='store_true')
    parser.add_argument('--json_path', help='Указать свой путь к *.json файлу с результатами', default='')
    args = parser.parse_args()

    books_list = []
    book_id = 0

    for page_id in range(args.start_page, args.end_page):
        fantasy_books_url = "http://tululu.org/l55/{}/".format(page_id)
        response = requests.get(fantasy_books_url, allow_redirects=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        link_tags = soup.select("table.d_book")
        for tag in link_tags:
            book_id += 1
            book_url = tag.select_one("a")["href"]
            full_book_url = urljoin(fantasy_books_url, book_url)
            response = requests.get(full_book_url, allow_redirects=False)
            response.raise_for_status()
            try:
                check_redirect(response)
            except requests.exceptions.HTTPError as error:
                logging.warning(f"Обнаружен редирект по ссылке {full_book_url}, книга пропущена")
                continue
            book_information = create_book_information(response.text, full_book_url)
            if not args.skip_imgs:
                filename = f"{book_id}. {book_information['img_src'].split('/')[-1]}"
                folder = os.path.join(args.dest_folder, "images")
                os.makedirs(folder, exist_ok=True)
                path = os.path.join(folder, filename)
                download_file(book_information["img_src"], path)
            download_book_url = 'http://tululu.org/txt.php?id={}'.format(book_url[2:-1])
            if not args.skip_txt:
                filename = f"{book_id}. {book_information['title']}"
                sanitized_filename = sanitize_filename(filename)
                folder = os.path.join(args.dest_folder, "books")
                os.makedirs(folder, exist_ok=True)
                path = os.path.join(folder, f'{sanitized_filename}.txt')
                download_file(download_book_url, path)
            books_list.append(book_information)

    os.makedirs("{}{}".format(args.dest_folder, args.json_path), exist_ok=True)

    with open("{}{}books_info.json".format(args.dest_folder, args.json_path), "w") as my_file:
        json.dump(books_list, my_file)
