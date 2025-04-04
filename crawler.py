import requests
from bs4 import BeautifulSoup
import sys
import os
from urllib.parse import urljoin, urlparse, urlunparse, unquote
import time
import re
from collections import deque


def ensure_files_dir_exists():
    if not os.path.exists('files'):
        os.makedirs('files')


def normalize_url(url):
    decoded_url = unquote(url)
    parsed = urlparse(decoded_url)
    clean_path = parsed.path.split('#')[0].split('?')[0]
    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc,
        clean_path,
        '', '', ''
    ))
    return normalized


def is_russian_page(text):
    if not text:
        return False

    russian_chars = len(re.findall('[а-яА-ЯёЁ]', text))
    english_chars = len(re.findall('[a-zA-Z]', text))

    return russian_chars > english_chars * 2


def get_text_from_url(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        response = requests.get(url, timeout=10, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        for element in soup(['footer', 'nav', 'script', 'style']):
            element.decompose()

        text = soup.get_text(separator=' ', strip=True)
        return text

    except Exception as e:
        print(f"Ошибка загрузки {url}: {e}")
        return None


def extract_links(base_url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(base_url, timeout=10, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = set()

        for a in soup.find_all('a', href=True):
            href = a['href']
            absolute_url = urljoin(base_url, href)
            normalized = normalize_url(absolute_url)

            if normalized and normalized.startswith('http'):
                links.add(normalized)

        return list(links)

    except Exception as e:
        print(f"Ошибка извлечения ссылки из {base_url}: {e}")
        return []


def main(start_urls):
    ensure_files_dir_exists()
    visited = set()
    to_visit = deque()
    doc_count = 0
    index = []

    for url in start_urls:
        normalized = normalize_url(url)
        if normalized and normalized not in visited:
            to_visit.append(normalized)

    current_level = len(to_visit)
    next_level = 0

    while doc_count < 100 and to_visit:
        url = to_visit.popleft()
        current_level -= 1

        if url in visited:
            continue

        print(f"\nОбрабатывается ({doc_count}/100): {url}")
        text = get_text_from_url(url)

        # Проверяем, русскоязычная ли страница
        if not text or not is_russian_page(text):
            print(f"Страница {url} не является русскоязычной")
            visited.add(url)
            continue

        word_count = len(text.split())
        print(f"Всего {word_count} слов в {url}")

        if word_count >= 1000:
            doc_count += 1
            filename = f"files/doc_{doc_count}.txt"

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(text)

            index.append(f"{doc_count} {url}")

        visited.add(url)
        time.sleep(1)

        if doc_count < 100 and text and is_russian_page(text):
            links = extract_links(url)
            for link in links:
                if link not in visited and link not in to_visit:
                    to_visit.append(link)
                    next_level += 1

        if current_level == 0:
            current_level = next_level
            next_level = 0
            print(f"\nПереход на следующий уровень, URL в очереди: {current_level}")

    with open("index.txt", 'w', encoding='utf-8') as f:
        f.write("\n".join(index))
    print(f"\nСохранено {doc_count} файлов")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python crawler.py <URL1> <URL2> ...")
        sys.exit(1)

    main(sys.argv[1:])