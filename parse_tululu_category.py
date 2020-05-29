import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

for page_id in range(1, 11):
    url = "http://tululu.org/l55/{}/".format(page_id)
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    link_tags = soup.find_all("table", border="0")
    for tag in link_tags:
        print(urljoin(url, tag.find("a")["href"]))