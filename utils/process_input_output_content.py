import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from utils.logic_parser import get_tag_list


def get_url_content(url):
    try:
        response = requests.get(url, allow_redirects=True, timeout=1000)
        response.raise_for_status()
        return response.text
    except RequestException as e:
        return None


def get_text_from(html_content, tags):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        texts = []
        tag_list = get_tag_list(tags)
        for tag in soup.find_all(tag_list):
            texts.append(tag.get_text(strip=True).split())

        return [list(x) for x in set(tuple(x) for x in texts)]

    except Exception as e:
        return None


def write_products_to_file(prods, url, aux_output_file):
    with open(aux_output_file, 'a') as prods_out:
        prods_out.write(url)
        for prod in prods:
            prods_out.write(f', {" ".join(prod)}')
        prods_out.write("\n")


def write_sets_records_to_file(tagger_results_list, output_file):
    with open(output_file, 'w') as train_set_file:
        for l in tagger_results_list:
            train_set_file.write(f'{l}\n')
