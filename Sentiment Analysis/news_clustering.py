import argparse
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import ParameterGrid
import csv
import numpy as np

runParams = {'tfidf_maxdf':         [0.5],
             'input_file':          ['./data/articles.csv'],
             'story_threshold':     [0.26],
             'process_date':        [''],
             'parts_of_speech':     [['PROPER', 'VERB']],
             'lemma_conversion':    [False],
             'ngram_conversion':    [3],
             'tfidf_binary':        [False],
             'tfidf_norm':          ['12'],
             'nlp_library':         ['nltk'],
             'max_length':          [50],
             'stop_words_file':     ['/data/stopWords.txt'],
             'tfidf_mindf':         [2],
             'display_graph':       [True],
             'article_stats':       [False]}

# Load and initialize required NLP libraries
pos_nlp_mapping = {}
nl = None
wordnet_lemmaitzer = None
nlp = None

if 'spaCy' in runParams['nlp_library']:
    import spacy
    nlp = spacy.load('en')
    pos_nlp_mapping['spaCy'] = {'VERB': ['VERB'],
                                'PROPER': ['PROPN'], 'COMMON': ['NOUN']}

if 'nltk' in runParams['nlp_library']:
    import nltk as nl
    if True in runParams['lemma_conversion']:
        from nltk.stem import WordNetLemmatizer
        wordnet_lemmaitzer = WordNetLemmatizer()
    else:
        wordnet_lemmaitzer = None
    pos_nlp_mapping['nltk'] = {'VERB': ['VB', 'VBD', 'VBG', 'VBN', 'VBZ'], 'PROPER': [
        'NNP', 'NNPS'], 'COMMON': ['NN', 'NNS']}

def getInputDataAndDisplayStats(filename, processDate, printSummary=False):

    df = pd.read_csv(filename)
    df = df.drop_duplicates('text')
    df = df[~df['text'].isnull()]

    if printSummary:
        print("\nArticle counts by publisher:")
        print(df['publication'].value_counts())

        print("\Article counts by date:")
        print(df['date'].value_counts())

    
    #


