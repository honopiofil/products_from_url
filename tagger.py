from bs4 import BeautifulSoup
from tqdm import tqdm
from argparse import ArgumentParser
from localconfig import config
from utils.logic_parser import get_tag_list, product_rule_parser
from utils.process_input_output_content import (get_url_content, get_text_from,
                                                write_sets_records_to_file, write_products_to_file)


def extract_product_text(html_content, rule_string, not_product_words):
    """Search for HTML tags that meet rules. The rules must be defined in conf/tagger.ini.
    Single product is returned as list of tokens - eventually a list of lists is returned."""
    products = []
    if html_content is not None:
        soup = BeautifulSoup(html_content, 'html.parser')

        product_tags = soup.find_all(lambda tag: eval(rule_string))

        # Wypisz tekst z każdego znalezionego tagu, ale tylko jeśli tekst znajduje się bezpośrednio w tagu (nie jest zagnieżdżony)
        for tag in product_tags:
            if (tag.string and
                    tag.string.strip() and
                    set(tag.string.lower().strip().split()).isdisjoint(not_product_words)):
                products.append(tag.string.strip().split())

    # return only unique elements from list of list
    return [list(x) for x in set(tuple(x) for x in products)]


def _find_words_positions(phrase_list, text_list):
    positions = []
    i = 0
    while i < len(text_list):
        if text_list[i:i + len(phrase_list)] == phrase_list:
            positions += list(range(i, i + len(phrase_list)))
            i += len(phrase_list)
        else:
            i += 1
    return set(positions)


def tag_products_on_site_text(products_list, text_list, url, tagger_results_list):
    """Tag all found text on the website with tags: 'pp' for words belonging to phrases denoting products,
    '00' - for all other words. The result is added to the tagger_results_list."""

    ex_counter = 0
    for line in text_list:
        res = set()
        for prod in products_list:
            res.update(_find_words_positions(prod, line))
        tag_list = ['pp' if i in res else '00' for i in range(len(line))]
        tagger_results_list.append(f'{url}_{ex_counter},"{line}","{tag_list}"')
        ex_counter += 1


def process_single_url(url,
                       rule_string,
                       not_product_words,
                       aux_output_file,
                       tagger_results_list):
    url = url.strip()
    html_content = get_url_content(url)
    products = extract_product_text(html_content, rule_string, not_product_words)
    write_products_to_file(products, url, aux_output_file)
    tags = config.product_rules.tag_name_rule
    whole_site_text = get_text_from(html_content, tags)
    if whole_site_text:
        tag_products_on_site_text(products, whole_site_text, url, tagger_results_list)


def process_urls_from_file(input_urls,
                           product_rule,
                           not_product_words,
                           output,
                           aux_output):
    with open(input_urls, 'r') as file:
        urls = file.readlines()

    tagger_results_list = []
    for url in tqdm(urls[40:50]):
        process_single_url(url,
                           product_rule,
                           not_product_words,
                           aux_output,
                           tagger_results_list)

    write_sets_records_to_file(tagger_results_list, output)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('input_urls')
    parser.add_argument('urls_prods_output')
    parser.add_argument('urls_info_output')
    args = parser.parse_args()
    
    config.read('./conf/tagger.ini')
    
    with open(args.urls_info_output, 'w'):
        pass
    
    not_product_words = set(config.product_rules.not_product_names.split(','))
    product_rule = product_rule_parser(config.product_rules.tag_name_rule, config.product_rules.tag_attribute_rule)
    
    process_urls_from_file(args.input_urls,
                           product_rule,
                           not_product_words,
                           args.urls_prods_output,
                           args.urls_info_output
                           )
