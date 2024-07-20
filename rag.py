import json
import pandas as pd
import datetime
import re
import string
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def wrangle_data(filepath: str) -> pd.DataFrame:
    """
    This function reads in the data from the filepath, cleans it and returns a pandas dataframe
    
    Args:
    filepath: str: a path to the json file
    
    Returns:
    df: pd.DataFrame: a pandas dataframe with the cleaned data
    
    """
    # load data
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Get article body, urls and titles
    doc = {
        'article_title': data['article_link_title'],
        'article_links': data['article_links'],
        'article_body': data['article_body'],
    }


    # Store the data in a pandas dataframe
    df = pd.DataFrame(doc)
    
    
    ## Clean article title
    # Remove the forward-slash character
    df['article_title_cleaned'] = df['article_title'].str.replace(r"\/","")

    # Remove punctuation
    df['article_title_cleaned'] = df['article_title_cleaned'].str.translate(string.punctuation)

    # Remove digits
    df['article_title_cleaned'] = df['article_title_cleaned'].str.replace(r"\d+","")

    # Remove running spaces
    df['article_title_cleaned'] = df['article_title_cleaned'].str.replace(r"\s{2,}","")

    # Make the text lowercase
    df['article_title_cleaned'] = df['article_title_cleaned'].str.lower()
    
    ## Clean article body

    # Remove the forward-slash character
    df['article_body_cleaned'] = df['article_body'].str.replace(r"\/","")

    # Remove punctuation
    df['article_body_cleaned'] = df['article_body_cleaned'].str.translate(string.punctuation)

    # Remove digits
    df['article_body_cleaned'] = df['article_body_cleaned'].str.replace(r"\d+","")

    # Remove running spaces
    df['article_body_cleaned'] = df['article_body_cleaned'].str.replace(r"\s{2,}","")

    # Make the text lowercase
    df['article_body_cleaned'] = df['article_body_cleaned'].str.lower()
    
    return df


doc_df = wrangle_data('data/stack-help_data.json')


for article in doc_df['article_title_cleaned']:
    print(article)
    print('\n')
# print(type(docs), len(docs_urls), len(docs_titles))
