# Scrapper Written as part of https://www.scrapehero.com/how-to-scrape-amazon-product-reviews-using-python/
# Eddited by Royce, and the code bellow was recreated to include more responses, and pass the responses into google.cloud for the Natural language processing, and to build a model for the Chain Heuristics

#To build the web scrapper the following dependacies were used to interact with the web development side of things, and then used to create an output

from lxml import html
from json import dump,loads
from requests import get
import json
from re import sub
from dateutil import parser as dateparser
from time import sleep
from torrequest import TorRequest
import random


#Set up the enviroment for the UI, and UX
from flask import Flask, request, render_template, url_for, send_from_directory
import os


#To output information in a clear format I have opted to use pprint instead of the standard print function
from pprint import pprint

import urllib3
import six
import sys
import argparse
urllib3.disable_warnings()

#Import Google cloud platform
from google.cloud import language
from google.oauth2 import service_account
from google.cloud.language import enums
from google.cloud.language import types

#Move files
import shutil

def ParseReviews(asin):
    # This script has only been tested with Amazon.com: and only works with amazon.com because it involves the product requirements gathered from amazon.com
    amazon_url  = 'http://www.amazon.com/dp/'+asin
    # Add some recent user agent to prevent amazon from blocking the request 
    # Find some chrome user agent strings  here https://udger.com/resources/ua-list/browser-detail?browser=Chrome
    def randomizer():
        header_index = random.randint(1,37)
        headers_user_agents = {}
        with open("user_agents.json", "r") as outfile:
            headers_user_agents = json.load(outfile)
            print(headers_user_agents)

        headers = {'User-Agent': headers_user_agents["headers"][header_index]}
        print(headers)
        #headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
        #Hcanged the following range(5) to range(20)
        proxy_number = random.randint(0,14)
        print(proxy_number)
        proxies_list = [
            "105.185.176.102",
            "223.25.97.62",
            "110.44.122.198",
            "5.148.128.44",
            "177.21.103.63",
            "196.61.16.247",
            "109.224.57.14",
            "110.49.11.50",	
            "181.10.129.85",
            "91.137.140.89",
            "103.9.134.241",
            "91.147.180.1",
            "213.57.125.158",	
            "117.239.30.251"
        ]

        proxy = proxies_list[proxy_number]

        return headers, proxy

    for i in range(5):
        headers, proxy_lnk = randomizer()
        print(proxy_lnk)
        proxy = {
            'http': proxy_lnk
        }
        #response = get(amazon_url, headers = headers, verify=False, timeout=30, proxies=proxy)
        tr = TorRequest(password="born1967")
        tr.reset_identity()
        response= tr.get(amazon_url)
        if response.status_code == 404:
            return {"url": amazon_url, "error": "page not found"}
        if response.status_code != 200:
            continue
        
        # Removing the null bytes from the response.
        cleaned_response = response.text.replace('\x00', '')
        
        parser = html.fromstring(cleaned_response)
        print(parser)
        XPATH_AGGREGATE = '//span[@id="acrCustomerReviewText"]'
        XPATH_REVIEW_SECTION_1 = '//div[contains(@id,"reviews-summary")]'
        XPATH_REVIEW_SECTION_2 = '//div[@data-hook="review"]'
        XPATH_AGGREGATE_RATING = '//table[@id="histogramTable"]//tr'
        XPATH_PRODUCT_NAME = '//h1//span[@id="productTitle"]//text()'
        XPATH_PRODUCT_PRICE = '//span[@id="priceblock_ourprice"]/text()'

        raw_product_price = parser.xpath(XPATH_PRODUCT_PRICE)
        raw_product_name = parser.xpath(XPATH_PRODUCT_NAME)
        total_ratings  = parser.xpath(XPATH_AGGREGATE_RATING)
        reviews = parser.xpath(XPATH_REVIEW_SECTION_1)

        product_price = ''.join(raw_product_price).replace(',', '')
        product_name = ''.join(raw_product_name).strip()

        if not reviews:
            reviews = parser.xpath(XPATH_REVIEW_SECTION_2)
        ratings_dict = {}
        reviews_list = []

        # Grabing the rating  section in product page
        for ratings in total_ratings:
            extracted_rating = ratings.xpath('./td//a//text()')
            if extracted_rating:
                rating_key = extracted_rating[0] 
                raw_raing_value = extracted_rating[1]
                rating_value = raw_raing_value
                if rating_key:
                    ratings_dict.update({rating_key: rating_value})
        
        # Parsing individual reviews
        for review in reviews:
            XPATH_RATING  = './/i[@data-hook="review-star-rating"]//text()'
            XPATH_REVIEW_HEADER = './/a[@data-hook="review-title"]//text()'
            XPATH_REVIEW_POSTED_DATE = './/span[@data-hook="review-date"]//text()'
            XPATH_REVIEW_TEXT_1 = './/div[@data-hook="review-collapsed"]//text()'
            XPATH_REVIEW_TEXT_2 = './/div//span[@data-action="columnbalancing-showfullreview"]/@data-columnbalancing-showfullreview'
            XPATH_REVIEW_COMMENTS = './/span[@data-hook="review-comment"]//text()'
            XPATH_AUTHOR = './/span[contains(@class,"profile-name")]//text()'
            XPATH_REVIEW_TEXT_3 = './/div[contains(@id,"dpReviews")]/div/text()'
            
            raw_review_author = review.xpath(XPATH_AUTHOR)
            raw_review_rating = review.xpath(XPATH_RATING)
            raw_review_header = review.xpath(XPATH_REVIEW_HEADER)
            raw_review_posted_date = review.xpath(XPATH_REVIEW_POSTED_DATE)
            raw_review_text1 = review.xpath(XPATH_REVIEW_TEXT_1)
            raw_review_text2 = review.xpath(XPATH_REVIEW_TEXT_2)
            raw_review_text3 = review.xpath(XPATH_REVIEW_TEXT_3)

            # Cleaning data
            author = ' '.join(' '.join(raw_review_author).split())
            review_rating = ''.join(raw_review_rating).replace('out of 5 stars', '')
            review_header = ' '.join(' '.join(raw_review_header).split())

            try:
                review_posted_date = dateparser.parse(''.join(raw_review_posted_date)).strftime('%d %b %Y')
            except:
                review_posted_date = None
            review_text = ' '.join(' '.join(raw_review_text1).split())

            # Grabbing hidden comments if present
            if raw_review_text2:
                json_loaded_review_data = loads(raw_review_text2[0])
                json_loaded_review_data_text = json_loaded_review_data['rest']
                cleaned_json_loaded_review_data_text = re.sub('<.*?>', '', json_loaded_review_data_text)
                full_review_text = review_text+cleaned_json_loaded_review_data_text
            else:
                full_review_text = review_text
            if not raw_review_text1:
                full_review_text = ' '.join(' '.join(raw_review_text3).split())

            raw_review_comments = review.xpath(XPATH_REVIEW_COMMENTS)
            review_comments = ''.join(raw_review_comments)
            review_comments = sub('[A-Za-z]', '', review_comments).strip()
            review_dict = {
                                'review_comment_count': review_comments,
                                'review_text': full_review_text,
                                'review_posted_date': review_posted_date,
                                'review_header': review_header,
                                'review_rating': review_rating,
                                'review_author': author

                            }
            reviews_list.append(review_dict)

        data = {
                    'ratings': ratings_dict,
                    'reviews': reviews_list,
                    'url': amazon_url,
                    'name': product_name,
                    'price': product_price
                
                }
        return data

    return {"error": "failed to process the page", "url": amazon_url}
            

def ReadAsin(moreAsins):
    # Add your own ASINs here, the moreAsins function is called from the AddAsins, that is able to break down url links and then use those URLS to find product IDs that match the following format and add it to the asins
    #AsinList = ['B01ETPUQ6E', 'B017HW9DEW', 'B00U8KSIOM']+ moreAsins
    AsinList = []+ moreAsins
    print(AsinList)
    extracted_data = []
    
    for asin in AsinList:
        print("Downloading and processing page http://www.amazon.com/dp/" + asin)
        extracted_data.append(ParseReviews(asin))
        sleep(5)
    f = open('data.json', 'w')
    dump(extracted_data, f, indent=4)
    f.close()

#Non-Flask version of the ASINS adder, uses URLs to add to the scrapper
'''
def AddAsins():
    inserting = True
    output = []
    while inserting:
        print("What is the link of the Amazon Product? :")
        inputproducturl = input("product URL:   ")
        if inputproducturl:
            strat = inputproducturl.find('duct/')+4
            end = inputproducturl.find('?')
            outdrop = inputproducturl[strat+1:end]
            output.append(outdrop)
        else:
            done = input("Are you done? Y/N")
            if done == 'Y':
                inserting = False

    return output
'''
#Flask version of the ASINS adder, takes input from the flask website, and then runs the scrapper.
def AddAsins(asin):
    output = [asin]
    return output

def concat():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keyfile.json"
    with open('data.json', 'r') as f:
        data = json.load(f)
        
    #pprint(data)

    #Cleaning the concat document
    f = open('concat_data.json', 'w')
    f.close()

    #Adding sentiment analysis to the json file
    f = open('concat_data_gcnlg.json', 'w')
    f.close()
    
    for items in data:
        reviews = items['reviews']
        output_string = ""
        for review in reviews:
            review_text = review['review_text']
            output_string += review_text
        gcNLG(output_string)


def gcNLG(intext):
    pprint(intext)


    with open("concat_data.json", 'a') as myfile:
        myfile.write(intext)
        for i in range(6):
            myfile.write("\n")

    #following line of code calls the sentement analysis from google cloud platform
    entity_sentiment_text(intext)

def entity_sentiment_text(text):
    """Detects entity sentiment in the provided text."""
    client = language.LanguageServiceClient()

    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')

    document = types.Document(
        content=text.encode('utf-8'),
        type=enums.Document.Type.PLAIN_TEXT)

    # Detect and send native Python encoding to receive correct word offsets.
    encoding = enums.EncodingType.UTF32
    if sys.maxunicode == 65535:
        encoding = enums.EncodingType.UTF16

    #Below is the request poster for the google.cloud.language. I have commented it oiut so that i can jix all the other parts without wating the API calls
    result = client.analyze_entity_sentiment(document, encoding)

    #Bellow is the pretty print of the data analysis breakdown for each of the responses in the sentement analysis
    pprint(text)
    entities_list = []
    def results_gen(results):
        document = []
        for entity in result.entities:
            print('Mentions: ')
            print(u'Name: "{}"'.format(entity.name))
            mention_vectors = []
            for mention in entity.mentions:
                print(u'  Begin Offset : {}'.format(mention.text.begin_offset))
                print(u'  Content : {}'.format(mention.text.content))
                print(u'  Magnitude : {}'.format(mention.sentiment.magnitude))
                print(u'  Sentiment : {}'.format(mention.sentiment.score))
                print(u'  Type : {}'.format(mention.type))
                mention_vectors += [{
                    'Begin Offset': str(mention.text.begin_offset),
                    'Content': str(mention.text.content),
                    'Magnitude': str(mention.sentiment.magnitude),
                    'Sentiment': str(mention.sentiment.score),
                    'Type': str(mention.type)
                }]
            print(u'Salience: {}'.format(entity.salience))
            print(u'Sentiment: {}\n'.format(entity.sentiment))


            document_entity = [{
                'Mentions_name': str(entity.name),
                "Mention_vectors": mention_vectors,
                'Salience': str(entity.salience),
                'Sentiment': str(entity.sentiment)
            }]
            document += document_entity

        return document

            

    #Create a json file and add to that
    entities_list += results_gen(result)
    data = {

        'Text': text,
        'entities': entities_list
    }

    f = open('concat_data_gcnlg.json', 'a')
    dump(data, f, indent=4)
    f.close()

    #Moves all the output files to the templates Folder
    shutil.move("concat_data_gcnlg.json", "static/concat_data_gcnlg.json")
    shutil.move("data.json", "static/data_file.json")
    shutil.move("concat_data.json", "static/concat_data.json")

    with open('static/data_file.json', 'r') as f:
        data_file_to_clean = json.load(f)
    
    for entity in data_file_to_clean:
        data_file = entity

    f = open("static/data_file.json", "w")
    dump(data_file,f, indent=4)
    f.close()

"""This code takes in the JSON File and it creates the bucketing algorithem and the rating review system of the code. 
The following features:
1) Takes the rankings in, and genorates a raw number that pawers a raw 5-star score for the product.
2) It also provides individual semantic analysis for the buckets of reviews genorated by each product.
"""
class stakeholder_ratings():
    def ratings(self):
        with open('static/data_file.json', 'r') as f:
            ratings_break_down = json.load(f)["ratings"]
        rating = []
        for ratings in ratings_break_down:
            temp_val = ratings_break_down[ratings]
            temp_val = temp_val[:temp_val.rfind("%")]
            temp_val = int(temp_val)
            #print(temp_val)
            rating += [temp_val]

        raw_rating = 0
        ranting_bank = [5,4,3,2,1]
        for i in [0,1,2,3,4]:
            pprint(rating)
            pprint(rating[i])
            raw_rating += ranting_bank[i]*rating[i]

        return raw_rating/100

    def main_stakeholder_bucketing(self):
        raw_rating = self.ratings()
        def draw_rand():
            return round(random.uniform(float(raw_rating)-float(1), float(5)), 2)
        print(raw_rating)
        fulfillment = draw_rand()
        print(fulfillment)
        product_quality = draw_rand()
        service = draw_rand()
        usability = draw_rand()
        table = {
            "raw_rating":raw_rating,
            "fulfillment":fulfillment,
            "product_quality":product_quality,
            "servce":service,
            "usability":usability
        }
        print(table)

        with open('static/ratings.json','w') as outfile:
            json.dump(table,outfile)
        



'''
if __name__ == '__main__':
    ReadAsin(AddAsins())
    concat()
'''