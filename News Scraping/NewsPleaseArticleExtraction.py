import difflib
from itertools import accumulate, chain, repeat, tee
import pickle
import pandas as pd
from newsplease import NewsPlease
import csv
import random
import matplotlib

filepath = r'Insight/news-lens'

with open(r'{}/link_file.txt'.format(filepath)) as f:
    news_links = [line.replace("\n", "") for line in f]


def chuck(xs, n):
    assert n > 0
    L = len(xs)
    s, r = divmod(L, n)
    widths = chain(repeat(s+1, r), repeat(s, n-r))
    offsets = accumulate(chain((0,), widths))
    b, e = tee(offsets)
    next(e)
    return [xs[s] for s in map(slice, b, e)]


batch = chuck(news_links, 221)


def article_crawler():
    # crawler
    n = 0
    for i in range(0, len(batch)):
        try:
            slice = batch[i]
            # print slice
            print(n)
            slice_name = str(i) + '-NewsPlease-articleCrawl.p'
            article_information = NewsPlease.from_urls(slice)
            print(article_information)
            pickle.dump(article_information, open(slice_name, 'wb'))
            n += 1
        except:
            continue


article_crawler()


def make_unique(url_list):
    # Not order preserving
    unique = set(url_list)
    return list(unique)


def check_data(filepath):
    scraped = []
    not_scraped = []

    for i in range(0, 220):
        try:
            file_path = filepath+"/crawl/"
            open_crawl = pickle.load(open(file_path + str(i)
                                          + "-NewsPlease-articleCrawl.p", "rb"))
            for url in open_crawl:
                text = open_crawl[str(url)].maintext
                if text == None:
                    not_scraped.append(url)
                else:
                    scraped.append(url)
        except FileNotFoundError:
            continue

    scraped = make_unique(scraped)
    return scraped, not_scraped


success, fail = check_data(filepath)


def percentage(part, whole):
    percent = 100 * float(part)/float(whole)
    format = "{0:.2f}".format(percent)
    return format+'%'


print("The extraction process yield "
      + str(len(success)) + " articles, or "
      + percentage(len(success), len(news_links))
      + " of the total.")


def get_data(filepath):
    news_dict = {}

    remove_list = ['www.', '.com', '.gov', '.org', 'beta.', ',eu',
                   '.co.uk', 'europe', 'gma', 'blogs', 'in.', 'm.',
                   'eclipse2017.', 'money', 'insider', 'news.', 'finance.'
                   'www1.']

    for i in range(0, 220):
        try:
            file_path = filepath + "/crawl/"
            open_crawl = pickle.load(open(file_path+str(i)
                                          + "-NewsPlease-articleCrawl.p", "rb"))

            for url in open_crawl:
                text = open_crawl[str(url)].maintext
                if text != None:
                    title = open_crawl[str(url)].title

                    source = open_crawl[str(url)].source_domain

                    for seq in remove_list:
                        if seq in source:
                            source = source.replace(seq, "")

                    date = open_crawl[str(url)].date_publish

                    news_dict[str(url)] = [source, title, date, text]

        except FileNotFoundError:
            continue

    return news_dict


all_news = get_data(filepath)


def get_source(all_news):
    news_sources = {}
    for article in all_news:
        source = all_news[article][0]
        if source not in news_sources:
            news_sources[source] = 1
        else:
            news_sources[source] += 1
    return news_sources


check_sources = {'CNN (Web News)': 205, 'USA Today': 136, 'Reuters': 99, 'The Wall Street Journal': 129, 'Vox': 85, 'Free Beacon': 5, 'Washington Times': 181, 'ABC News': 20, 'The Hill': 192, 'The New York Times': 215, 'The Washington Post': 257, 'The Washington Examiner': 93, 'Fox News': 345, 'Buzz Feed': 6, 'HuffPost': 151, 'The Los Angeles Times': 27, 'CBN': 48, 'National Review': 36, 'The Atlantic': 14, 'NPR': 76, 'The Boston Globe': 3, 'News Max': 46, 'AP': 5, 'Business insider': 11, 'reason': 23, 'time magazine': 10, 'bloomberg': 27, 'daily caller': 28, 'town hall': 105, 'politico': 92, 'daily kos': 35, 'cnet': 1, 'newsweek': 17, 'bbc': 69, 'bustle': 6, 'breitbart': 59, 'NBCNews.com': 34, 'CBS News': 25, 'daily mail': 5, 'the daily beast': 25, 'The Daily Wire': 3, 'slate': 11, 'boston herald': 1, 'axios': 3, 'yahoo': 5, 'new york daily news': 6,
                 'economist': 1, 'mediaite': 3, 'The Heritage Foundation': 1, 'the guardian': 55, 'new york magazine': 6, 'chicago tribune': 13, 'commentary magazine': 1, 'vice': 1, 'new yorker': 1, 'CNBC': 4, 'the blaze': 18, 'korea herald': 1, 'vanity fair': 8, 'the week': 13, 'american thinker': 1, 'PBS NewsHour': 2, 'think progress': 5, 'real clear politics': 5, 'SFGate': 2, 'mashable': 2, 'the verge': 1, 'salon': 20, 'daily press': 1, 'all sides': 5, 'mismatch': 1, 'living room conversations': 1, 'spectator': 14, 'WND.com': 1, 'redstate': 1, 'fox business': 4, 'democracy now': 5, 'Christian Science Monitor': 18, 'Pacific Standard': 1, 'scientific american': 1, 'MSNBC': 2, 'whitehouse': 1, 'forbes': 1, 'politics.blog.ajc': 1, 'the federalist': 2, 'life hacker': 1, 'hot air': 4, 'the intercept': 2, 'conservative hq': 1, 'fact check': 2, 'telegraph': 1}

bias_ratings = r"{}/allsides-media-bias-ratings.csv".format(filepath)

bias_dict = {}

with open(bias_ratings, mode='r') as infile:
    reader = csv.reader(infile)
    bias_dict = {rows[0]: rows[1] for rows in reader}

# assess string similiarity


def string_sim(a, b):
    seq = difflib.SequenceMatcher(None, a, b)
    sim = seq.ratio() * 100
    return sim


def replace_names(check_sources, bias_dict):
    real_source = {}

    for entry in check_sources:
        for source in bias_dict:

            sim = string_sim(entry, source)
            count = check_sources[entry]

            if entry not in real_source:
                real_source[entry] = [source, sim, count]

            else:
                if sim > real_source[entry][1]:
                    real_source[entry] = [source, sim, count]

    raw_data = {'News_Source': [], 'Bias': [], 'Article_Count': []}

    for key in real_source:
        new_key = real_source[key][0]
        new_count = real_source[key][2]

        bias = bias_dict[new_key]

        raw_data['News_Source'].append(new_key)
        raw_data['Article_Count'].append(new_count)
        raw_data['Bias'].append(bias)

    for bias_rating in raw_data['Bias']:
        if bias_rating == 'Mixed':
            bias_rating = bias_rating.replace('Mixed', 'Center')

    source_bias = pd.DataFrame(
        raw_data, columns=['News_Source', 'Bias', 'Article_Count'])

    return source_bias


updated_info = replace_names(check_sources, bias_dict)
updated_info.to_csv('news-corpus-info.csv', index=False)

# open original data file


def open_sesame(filepath):
    datafile = open(r'{}/allsides-content.csv'.format(filepath),
                    'r', encoding='utf-8')
    myreader = csv.reader(datafile)
    return myreader

# return dict of stored values


def fill_dict():
    read_in = {'date': [], 'main_headline': [], 'description': [], 'source': [],
               'bias': [], 'headline': [], 'link': []}

    i = 0
    for key in read_in:
        myreader2 = open_sesame(filepath)
        read_in[key] = [row[i] for row in myreader2][1:]
        i += 1

        # add info from NewsPlease crawl
    read_in['text'] = []
    for url in read_in['link']:
        try:
            read_in['text'].append(all_news[str(url)][3])
        except KeyError:
            read_in['text'].append('None')

    return read_in


formatted = fill_dict()

df = pd.DataFrame(formatted, columns=['date', 'main_headline', 'description',
                                      'source', 'bias', 'headline', 'link', 'text'])

df = df.drop(df[df.text == 'None'].index)
df = df.drop(df[df.text == 'Mixed'].index)
df.date = pd.to_datetime(df.date)

df['text_len'] = df.apply(lambda row: len(row.text), axis=1)
#df['id'] = [random.randint(2000, 7000) for k in df.index]

# drop any articles where text length > 20,000 and < 250 words
df = df.drop(df[df.text_len > 20000].index)
df = df.drop(df[df.text_len < 250].index)

# write to csv
df.to_csv('news-corpus-df.csv', index=False)

bybias = df.groupby('bias')
bybias['text_len'].describe()

df.groupby('bias').text_len.hist(alpha=0.4)

df['month_year'] = df.date.dt.to_period('M')

count_by_date = df.groupby(['month_year', 'bias']).text_len
count_by_date = count_by_date.describe()

count_by_date.to_csv('count_by_date.csv', index=False)

