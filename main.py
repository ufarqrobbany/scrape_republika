import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def get_publish_time(info):
    saat_ini = datetime.now()
    if 'jam' in info:
        return (saat_ini - timedelta(hours=int(info.split('-')[1].strip().split()[0]))).strftime("%A, %d %B %Y, %H:%M WIB")
    elif 'menit' in info:
        return (saat_ini - timedelta(minutes=int(info.split('-')[1].strip().split()[0]))).strftime("%A, %d %B %Y, %H:%M WIB")
    elif 'detik' in info:
        return (saat_ini - timedelta(seconds=int(info.split('-')[1].strip().split()[0]))).strftime("%A, %d %B %Y, %H:%M WIB")
    else:
        return info.split('-')[1].strip()


def scrape_republika_news():
    html_text = requests.get('https://www.republika.co.id/').text
    soup = BeautifulSoup(html_text, 'lxml')
    latest_news = soup.find('ul', class_="list-group wrap-latest")
    berita_list = []
    for news in latest_news.find_all('li', class_="list-group-item list-border conten1"):
        info = news.find('div', class_="date").text
        judul = news.h3.text.strip()
        link = news.a['href']
        kategori = info.split('-')[0].strip()
        waktu_publish = get_publish_time(info)
        waktu_scraping = datetime.now().strftime("%A, %d %B %Y, %H:%M WIB")
        berita_list.append({
            'judul': judul,
            'url': link,
            'kategori': kategori,
            'waktu_publish': waktu_publish,
            'waktu_scraping': waktu_scraping
        })
    return berita_list


def is_duplicate(news, existing_data):
    for item in existing_data:
        if item['judul'] == news['judul'] and item['url'] == news['url']:
            return True
    return False


def save_to_json(new_data):
    try:
        with open('berita.json', 'r') as json_file:
            existing_data = json.load(json_file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        existing_data = []

    if not existing_data or not isinstance(existing_data, list):
        all_data = new_data
    else:
        unique_data = [berita for berita in new_data if not is_duplicate(berita, existing_data)]
        all_data = existing_data + unique_data

    sorted_data = sorted(all_data, key=lambda x: datetime.strptime(x['waktu_publish'], "%A, %d %B %Y, %H:%M WIB"), reverse=True)

    with open('berita.json', 'w') as json_file:
        json.dump(sorted_data, json_file, indent=4)


if __name__ == "__main__":
    berita = scrape_republika_news()
    save_to_json(berita)
