#!/usr/bin/env python
# title                          :AllSidesMediaHeadlineCrawler.py (Part 1)
# description                    :This program extracts the necessary information for articles.
# author                         :Andre Sealy
# date                           :20200620
# version                        :1.0
# usage                          :python AllSidesMediaHeadlineCrawler.py
# notes                          :Run this code before running the News Please script
# python_version                 :3.7.6
# ==================================================================================================

# Import the modules needed to run the script
import requests
from bs4 import BeautifulSoup
import csv
import re
import socket
socket.socket

# creates a empty list to store the story pages from AllSides.com
pages = []
story = 'Immigration'

def get_seed(n):
    '''
    n defines the number of pages back to pull
    n=56 steps back to June 2016 (as of June 2018)
    '''
    for i in range(0, n+1):
        url = 'https://www.allsides.com/story/admin?tid=&field_story_topic_tid=' + \
            str(story) + '&page=' + str(i)
        pages.append(url)

get_seed(1)

# set up BeautifulSoup to run over All Sides Media
link_harvest = []

# helper function to harvest and parse pages
def soup_basics(item):
    page = requests.get(item)
    soup = BeautifulSoup(page.text, 'html.parser')
    return soup


def harvest_links(pages):
    '''
    runs the parser over submitted pages
    identifies headline link content in the extracted page
    appends relevant links to a list
    '''
    for item in pages:
        soup = soup_basics(item)

        # Pull all headlines from the featured stories under class 'view-content'
        story_headline_list = soup.find(class_='view-content')
        # Pull headline/link text from all instances of <a> tag
        story_list_items = story_headline_list.find_all('a')

        # harvest the headline and link information
        for story_headline in story_list_items:
            #headline = story_headline.contents[0]
            #headline = headline.encode("utf8").strip()
            link = 'https://www.allsides.com'+story_headline.get('href')
            if '/story/' in link:
                link_harvest.append(link)

harvest_links(pages)

# get all news article links
all_articles = []


def extract_articles(link_harvest):
    for link_content in link_harvest:
        soup = soup_basics(link_content)

        # locate relevant information within the extracted page
        substory_list = soup.find_all(class_='news-title')

        # loop through the different news sources within each major news story
        for i in range(0, len(substory_list)):
            substory_items = substory_list[i].find_all('a')
            for substory_headline in substory_items:
                link = substory_headline.get('href')
                all_articles.append(link)
                print(link)


extract_articles(link_harvest)

# save news article links to file
link_file = open('link_file.txt', 'w')

for item in all_articles:
    link_file.write("%s\n" % item)

# helper function to encode strings for csv


def csv_encoder(text_string):
    coded = text_string.encode("utf-8").strip()
    return coded

# extract all content


def extract_content(link_harvest):
    '''
    for each story, pulls the shared news headline, date, and summary description
    for each news source, identifies the source bias (liberal, conservative, center) & outgoing link
    uses re and .contents to clean harvested text
    writes collected, cleaned data to csv
    '''

    # open csv file to store info
    file = open('allsides-content.csv', 'w', newline="", encoding='utf-8')
    fileWriter = csv.writer(file)
    fileWriter.writerow(['Date', 'AllMedia_Headline', 'Description',
                         'Source_Name', 'Source_Bias', 'Source_Headline', 'Source_Link'])

    try:
        for link_content in link_harvest:
            soup = soup_basics(link_content)

            # locate relevant information within the extracted page
            story_headline = soup.find(class_='taxonomy-heading')
            story_date = soup.find(property='dc:date')
            story_description = soup.find(class_='story-id-page-description')
            substory_source = soup.find_all(class_='news-source')
            substory_bias = soup.find_all(class_='global-bias')
            substory_list = soup.find_all(class_='news-title')

            # loop through the different news sources within each major news story
            n = 0
            for i in range(0, len(substory_list)):
                substory_items = substory_list[i].find_all('a')
                for substory_headline in substory_items:

                    clean_date = story_date.contents[0]

                    clean_headline = re.sub(
                        '\W+', ' ', story_headline.contents[0])[1:][:-1]
                    clean_headline = csv_encoder(clean_headline)

                    try:
                        clean_description = str(
                            story_description.contents[1].text)
                    except IndexError:
                        clean_description = 'Null'

                    try:
                        clean_source = substory_source[n].contents[1]
                    except (AttributeError, IndexError):
                        clean_source = 'Unknown'

                    clean_bias = substory_bias[n]
                    clean_bias = re.sub(
                        '\W+', ' ', clean_bias.contents[0])[10:]
                    n = n+1

                    headline = substory_headline.contents[0]
                    headline = csv_encoder(headline)

                    link = substory_headline.get('href')

                    fileWriter.writerow(
                        [clean_date, clean_headline, clean_description, clean_source, clean_bias, headline, link])

    except socket.error as err:
        print('Socket connection error... Waiting 10 seconds to retry.')
        del self.sock
        time.sleep(10)
        try_count += 1

    file.close()


extract_content(link_harvest)
