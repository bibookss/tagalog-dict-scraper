import requests
from bs4 import BeautifulSoup
import multiprocessing
import re   
import csv 
import time

def preprocess_definition(definition):
    pos = re.findall(r'\w+\.', definition)
    pos = [p for p in pos if p != 'etc.' and p != 'coll.' and p != 'fig.' and p[0].isnumeric() == False]

    for p in pos:
        definition = definition.replace(p, 'MARKER')
    
    definition = definition.split('MARKER')    
    definition = definition[-1].split(';')

    definitions = []
    for d in definition:
        d = d.strip()
        if d != '':
            d = re.sub(r'\d+\.', '', d)
            definitions.append(d)

    return pos, definitions

def scrape_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            data = []

            word_list = soup.find('div', class_='word-list')
            for word_group in word_list.find_all('div', class_='word-group'):
                word = word_group.find('div', class_='word').find('a').text
                definition = word_group.find('div', class_='definition').find('p').text

                # pos, definition = preprocess_definition(definition)

                data.append({
                    'word': word,
                    'definition': definition,
                })

            return data
        else:
            print(f"Failed to fetch {url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred while scraping {url}: {str(e)}")
        return None

if __name__ == "__main__":
    base_url = 'https://tagalog.pinoydictionary.com/list/'
    urls = []

    for i in range(ord('a'), ord('z')+1):
        for j in range(1, 10):
            urls.append(base_url + chr(i) + f'?page={j}')

    start_time = time.time()

    num_processes = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=num_processes)

    results = pool.map(scrape_url, urls)
    pool.close()
    pool.join()

    csv_columns = ['word', 'pos', 'definition']
    csv_file = "tagalog.csv"

    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()

            for data in results:
                if data is not None:
                    for d in data:
                        writer.writerow(d)

        print(f"Successfully wrote {len(results)} rows to {csv_file}")
    except IOError:
        print("I/O error")

    print(f"Time taken: {time.time() - start_time} seconds")