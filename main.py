import requests
import os

if not os.path.exists("Books"):
    os.makedirs("Books")

for book_id in range(1, 11):
    book_url = 'http://tululu.org/txt.php?id={}'.format(book_id)
    response = requests.get(book_url, allow_redirects=False)
    response.raise_for_status()
    if response.status_code == 200:
        with open("Books/id{}.txt".format(book_id), "w") as my_file:
            my_file.write(response.text)