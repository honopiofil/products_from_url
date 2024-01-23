import gradio as gr
from transformers import pipeline
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('model_path')
args = parser.parse_args()

classifier = pipeline('ner',
                      model='/home/pawel/Documents/Furniture_Stores/FT_url_prods_bert-base-NER/checkpoint-2397',
                      aggregation_strategy='simple')
#classifier = pipeline('ner', model=args.model_path, aggregation_strategy='simple')

def get_url_content(url):
    try:
        response = requests.get(url, allow_redirects=True, timeout=1000)
        response.raise_for_status()
        return response.text
    except RequestException as e:
        return None


def get_text_from_website(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        texts = []
        for tag in soup.find_all(['a', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'title']):
            texts.append(tag.get_text(strip=True))
        return texts
    except Exception as e:
        return None


def inference(website_texts):
    inference_results = []
    for text in website_texts:
        for segment in classifier(text):
            if segment['entity_group'] == 'pp':
                inference_results.append(segment['word'].strip())
    return "\n".join(list(set(inference_results)))


def run(url):
    html_content = get_url_content(url)
    website_texts = get_text_from_website(html_content)
    if website_texts:
        found_products = inference(website_texts)
        return found_products
    else:
        return 'NO TEXT FOUND ON WEBSITE'


examples = ['https://hemisphereliving.com.au/products-on-sale/',
            'https://themodern.com.au/collections/on-sale',
            'https://brownandbeam.com/collections/furniture/products/howell-sideboard',
            'https://themodern.com.au/collections/bedroom-furniture',
            'https://modshop1.com/collections/all-modern-credenzas',
            'https://www.furnitureworldgalleries.com/product/alexvale-kora-leather-recliner/',
            'https://magnolialane.biz/collections/display-cabinet-stand/products/furo-2-door-cupboard',
            'https://www.yellowleafhammocks.com/collections#hanging-chair-hammocks',
            'https://sarahellison.com.au/products/alva-armchair-with-white-frame-in-bronte-whipped-cream',
            'https://www.bovafurniture.com/products/bedroom/nightstands/'
            ]


demo = gr.Interface(
    fn=run,
    inputs=["text"],
    outputs=["text"],
    examples=examples
)

demo.launch()
