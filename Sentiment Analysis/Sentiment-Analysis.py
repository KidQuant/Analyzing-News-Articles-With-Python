
#%% import pandas, time to impose rate limits, cloud library
import numpy as np
import time
from google.cloud.language import types
from google.cloud.language import enums
from google.cloud import language
import pandas as pd
import os
import re
import string
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
import seaborn as sns
import matplotlib.pyplot as plt

# Google Application Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "News Sentiment-fe10d899556f.json"

#%% read in file function


def read_data(filename):
    # read in csv
    df = pd.read_csv('news-corpus-df.csv')

    # drop text under 500 words
    df = df.drop(df[df.text_len < 500].index)

    # limit df content to bias, text, headline, and source
    df = df.loc[:, ['date', 'bias', 'headline', 'text', 'text_len',  'source']]

    # cleaning the 'bias' column of unnecessary white space
    df['bias'] = df['bias'].apply(lambda x: x.strip()) 

    # convert bias label to number
    df['bias'] = df['bias'].replace({'Left': 1, 'Center': 2, 'Right': 3})

    # classify without center biased news
    # new = new[new.bias != '2']

    return df

# read in file and preview
new = read_data('news-corpus-df.csv')
new.head()


#%% Instantiate a client
client = language.LanguageServiceClient()

# Gather sentiment score and magnitude data for each document
sentiment_list = []
magnitude_list = []

for i in range(0, len(new['text'].values)):
    # specify document type
    document = types.Document(
        content=new['text'].values[i], type=enums.Document.Type.PLAIN_TEXT)

    # detects the sentiment of the text
    sentiment = client.analyze_sentiment(document=document).document_sentiment
    sentiment_list.append(sentiment.score)
    magnitude_list.append(sentiment.magnitude)

    # wait a second to add delay to query
    time.sleep(.100)

# Add sentiment information to data frame
new = new.assign(sentiment=sentiment_list)
new = new.assign(magnitude=magnitude_list)
new.head(11)

#%%# equalize distribution over each bias class
center = new.loc[new['bias'] ==2]
right = new.loc[new['bias'] == 3]
left = new.loc[new['bias'] ==1]

new = center.append(right, ignore_index=True)
new = new.append(left, ignore_index=True)
new.head()

#%% strip texts of punctuation, boilerplate, and stop words


def text_prepare(text):
    """
        text: a string
        return: modified initial string
    """
    text = text.lower()
    text = text.replace('\n', ' ')

    letters = list(string.ascii_lowercase)
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    banned = ["’", "’", "“", "—", "”", "‘", "–", '#', '[', '/',
              '(', ')', '{', '}', '\\', '[', ']', '|', '@', ',', ';', '+', '-']
    banned = ''.join(banned) + string.punctuation + ''.join(numbers)
    boilerplate = ['  ', 'https', 'http', 'www', '’s', '―', '/', 'playback', 'get', 'mr', 'mrs', 'ms', 'dr', 'prof', 'news', 'report', 'unsubscribe', 'they', 'must', 'share', 'that', 'view', 'hide', 'copy', 'something', 'enlarge', 'reprint', 'read', '_', 'videos', 'autoplay', 'watched', 'press', '’ve', 'toggle', 'around', 'the', 's.', 'said', 'here©', 'ad', '#', 'andhis', 'click', 'r', 'device',
                   'contributed', 'advertisement', 'the washington', '&', 'follow', 'copyright', 'mrs.', 'photo', 'to', 'also', 'times', 'for', 'however', 'fox', 'this', 'copyright ©', 'ofs', 'just', 'wait', 'n’t', 'told', 'unsupported', 'i', 'caption', 'ms.', '’m', 'paste', '’re', 'replay', 'photos', 'mr.', '©', 'skip', 'watch', '2018', 'cut', 'llc', 'more', 'post', 'embed', 'blog', 'b.', 'associated', 'permission']
    stop_list = set(stopwords.words('english') + boilerplate + letters)

    translation_table = dict.fromkeys(map(ord, banned), ' ')
    text = text.translate(translation_table)
    text = re.sub(' +', ' ', text)
    text = ' '.join([word for word in text.split() if word not in stop_list])
    return text


# rewrite df with cleaned text
for i in range(0, len(new)):
    new.at[i, 'text'] = text_prepare(new.at[i, 'text'])
    new.at[i, 'headline'] = text_prepare(new.at[i, 'headline'])

new.head()

#%% save cleaned file to csv
new.to_csv('news-corpus-df-sent.csv', sep='\t', encoding='utf-8')

# convert bias numbers to labels
new['bias'] = new['bias'].replace({1: 'Left', 2: 'Center', 3: 'Right'})
sns.set_style('whitegrid')
# visualize sentiment in relation to bias

g = sns.FacetGrid(data=new, col='bias', col_wrap= 3, size=5 )
g.map(plt.hist, 'magnitude', bins=25)
plt.savefig('histogram.png', bbox_inches='tight')

#%%
plt.figure(figsize=(12,6))
sns.boxplot(x='bias', y='magnitude', data=new)

#%%
def densityplot(dimension):

    # Initialize the FaceGrid object
    sns.set(style="white", rc={'axes.facecolor': (0, 0, 0, 0)})
    pal = sns.cubehelix_palette(10, rot=-.25, light=.7)
    g = sns.FacetGrid(new, row="bias", hue="bias",
                      aspect=15, size=1, palette=pal)

    # Draw the densities in a few steps
    g.map(sns.kdeplot, dimension, clip_on=False,
          shade=True, alpha=1, lw=1.5, bw=.2)
    g.map(sns.kdeplot, dimension, clip_on=False, color='w', lw=2, bw=.2)
    g.map(plt.axhline, y=0, lw=2, clip_on=False)

    # Define and use a simple function to label the plot in axes coordinates
    def label(x, color, label):
        ax = plt.gca()
        ax.text(0, .2, label, fontweight='bold', color=color,
                ha='left', va='center', transform=ax.transAxes)

        # Set the subplot to overlap
        g.map(label, dimension)

        # Remove axes details that don't play will with overlap
        g.set_titles('')
        g.set(yticks=[])
        g.despine(bottom=True, left=True)

        return g

sentiment_plot = densityplot('sentiment') 
magnitude_plot = densityplot('magnitude')




# %%
