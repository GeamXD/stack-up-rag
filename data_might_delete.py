from bs4 import BeautifulSoup
import requests
import json


def make_request(url: str, selector: str) -> list:
    """
    Make a request to a webpage and return the tags that match the selector
    
    Args:
    url (str): The URL of the webpage
    selector (str): The CSS selector to use
    
    Returns:
    list: A list of tags that match the selector
    
    """
    try:
        # Make the request
        response = requests.get(url, timeout=5)
        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(response.content, 'lxml')
        # Extract all tags that match the selector
        tags = soup.select(selector)
        # Return the tags
        return tags
    # Handle exceptions
    except requests.exceptions.RequestException as e:
        # Print the error
        print(e)
        # Return an empty list
        return []

def concatenate_url(url: str, href: str, adjust=False) -> str:
    """
    Concatenate the base URL with the href attribute
    
    Args:
    base_url (str): The base URL
    href (str): The href attribute
    
    Returns:
    str: The concatenated URL
    
    """
    # if the href doesnt start with a /
    if adjust:
        # return the base URL concatenated with the href
        return url + href

    # If the href starts with a /
    else:
        # return the base URL concatenated with the href
        return url[:-1] + href

def get_urls_text(url: str, tags: list, adjust=False) -> tuple:
    """
    Get the URLs and text content from a list of tags
    
    Args:
    base_url (str): The base URL
    tags (list): A list of tags
    adjust (bool): A boolean to adjust the URL
    
    Returns:
    tuple: A tuple of URLs and text content
    
    """
    # Store main page links and Title
    urls = []
    text = []
    
    # Iterate through the tags and print href and text
    try:
        for tag in tags:
            # Get the href attribute
            href_url = concatenate_url(url, tag.get('href'), adjust=adjust)
            # Get the text content
            text_content = tag.get_text().replace('\n', '')
            # Append the href and text content to the lists
            urls.append(href_url)
            # Append the text content to the list
            text.append(text_content)
    except Exception as e:
        # Print the error
        print(e)
    
    # Return the URLs and text content
    return urls, text

#Fetch the webpage
BASE_URL = 'https://stackuphelpcentre.zendesk.com/'

# Store main page links and Title
main_tags = make_request(BASE_URL, 'a.blocks-item-link')
main_urls, main_urls_titles = get_urls_text(BASE_URL, main_tags)

# Store section tree url and title
section_tree_url = []
section_title = []

# Iterate through the main URLs
for main_url in main_urls:
    # Make a request to the main URL
    section_tags = make_request(main_url, 'section.section h2 a')
    # Get the section URLs and text content
    section_urls, section_titles = get_urls_text(BASE_URL, section_tags, adjust=False)
    # Append the section URLs and text content to the lists
    section_tree_url.append(section_urls)
    section_title.append(section_titles)


# Match section title to url respectively lazily
zipped_section_title_url = ((list(zip(titles, urls)) 
                             for titles, urls in zip(section_title, section_tree_url)))


# Extract section URL links only
section_links = (url for urls in section_tree_url for url in urls)

# Store article URLs and text content
article_urls = []
article_titles = []

# Iterate through the section URLs
for sec_tr_url in section_links:
    # Make a request to the section URL
    article_tags = make_request(sec_tr_url, 'a.article-list-link')
    # Get the articles URLs and text content
    article_url, article_title = get_urls_text(BASE_URL, article_tags, adjust=False)
    # Append the article URLs and text content to the lists
    article_urls.append(article_url)
    article_titles.append(article_title)

# Extract article URL links only
article_links = [url for urls in article_urls for url in urls]

# Extract article title only
article_body_title = [url for urls in article_titles for url in urls]

# Text content of the article
article_body = []

# Iterate through the article URLs
for article_url in article_links:
    # Make a request to the article URL
    article_tags = make_request(article_url, 'div.article-body')
    # Get the article text content
    article_text = [tag.get_text() for tag in article_tags][0]
    # Get article title
    article_title = article_body_title[article_links.index(article_url)]
    # Append the article text content to the list
    article_body.append((article_title, article_text.replace('\n', ' ').replace('\xa0', '')))


# Create a dictionary to store the data
data = {
    'main_urls_titles': main_urls_titles,
    'section_tree_url': [url for urls in section_tree_url for url in urls],
    'section_title': [title for titles in section_title for title in titles],
    'article_links': article_links,
    'article_link_title': article_body_title,
    'article_body': [body for title, body in article_body]
}

# Convert the dictionary to a JSON string
json_data = json.dumps(data)

# Save the JSON string to a file
with open('./data/stack-help_data.json', 'w', encoding='utf-8') as f:
    f.write(json_data)
