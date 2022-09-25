import requests
from bs4 import BeautifulSoup as BS
from datetime import datetime
import pandas as pd
from tqdm import tqdm

def get_soup(url):
    payload= {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    soup = BS(response.content, 'html.parser')
    return soup 

def parse_date(raw):
    months = {"január": "01", "február": "02", "március": "03", "április": "04", "május": "05",
    "június": "06", "július": "07", "augusztus": "08", "szeptember": "09", "október": "10", "november": "11", "december": "12"}
    splitted = raw.split('\n')[1].lstrip().split(' ')
    splitted[1] = months[splitted[1]]
    date = " ".join(splitted)
    return datetime.strptime(date, "%Y. %m %d. – %H:%M")

def parse_author(raw):
    return raw.split('\n')[4].lstrip()

def scrape_telex(pages=4432):
    data = {"date": [], "author": [], "highlight": [], "lead": [], "href": [], "language": []}

    for i in tqdm(range(pages)):
        url = f'https://telex.hu/archivum?oldal={i}'
        soup = get_soup(url)
        list_group = soup.find_all("div", {"class": "list__item__info"})
        for article in list_group:
            href = article.find('a', href=True)['href']
            if not href[1:8] == "english": #for now skipping english articles
                data["href"].append(href)
                data["language"].append("hu")
                raw = article.find(class_="article_date").text 
                try:
                    data["author"].append(parse_author(raw))
                except:
                    data["author"].append("")
                try:
                    data["date"].append(parse_date(raw)) 
                except:
                    data["date"].append(raw)
                data["highlight"].append(article.find(class_="hasHighlight").text)
                data["lead"].append(article.find('p', class_="list__item__lead hasHighlight").text)
    return pd.DataFrame(data=data)


if __name__ == "__main__":
    df = scrape_telex(4432)
    df.to_csv('telex.csv')

    #TODO: index, origo, 24, telex, blikk
        