import os
import json
import requests
from bs4 import BeautifulSoup

class WebScraper:
    """
    Scrapes the content of a webpage and saves it to a JSON file
    """
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.data = {
            'main_urls_titles': [],
            'section_tree_url': [],
            'section_title': [],
            'article_links': [],
            'article_link_title': [],
            'article_body': []
        }

    def make_request(self, url: str, selector: str) -> list:
        """
        Make a request to a webpage and return the tags that match the selector
        """
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.content, 'lxml')
            tags = soup.select(selector)
            return tags
        except requests.exceptions.RequestException as e:
            print(e)
            return []

    def concatenate_url(self, url: str, href: str, adjust=False) -> str:
        """
        Concatenate the base URL with the href attribute
        """
        if adjust:
            return url + href
        else:
            return url[:-1] + href

    def get_urls_text(self, url: str, tags: list, adjust=False) -> tuple:
        """
        Get the URLs and text content from a list of tags
        """
        urls = []
        text = []
        try:
            for tag in tags:
                href_url = self.concatenate_url(url, tag.get('href'), adjust=adjust)
                text_content = tag.get_text().replace('\n', '')
                urls.append(href_url)
                text.append(text_content)
        except Exception as e:
            print(e)
        return urls, text

    def scrape(self):
        """
        Perform the scraping process and populate the data dictionary
        """
        # Fetch the webpage
        main_tags = self.make_request(self.base_url, 'a.blocks-item-link')
        main_urls, main_urls_titles = self.get_urls_text(self.base_url, main_tags)
        self.data['main_urls_titles'] = main_urls_titles

        section_tree_url = []
        section_title = []

        for main_url in main_urls:
            section_tags = self.make_request(main_url, 'section.section h2 a')
            section_urls, section_titles = self.get_urls_text(self.base_url, section_tags, adjust=False)
            section_tree_url.append(section_urls)
            section_title.append(section_titles)

        zipped_section_title_url = ((list(zip(titles, urls)) 
                                     for titles, urls in zip(section_title, section_tree_url)))

        section_links = (url for urls in section_tree_url for url in urls)

        article_urls = []
        article_titles = []

        for sec_tr_url in section_links:
            article_tags = self.make_request(sec_tr_url, 'a.article-list-link')
            article_url, article_title = self.get_urls_text(self.base_url, article_tags, adjust=False)
            article_urls.append(article_url)
            article_titles.append(article_title)

        article_links = [url for urls in article_urls for url in urls]
        article_body_title = [url for urls in article_titles for url in urls]

        article_body = []

        for article_url in article_links:
            article_tags = self.make_request(article_url, 'div.article-body')
            article_text = [tag.get_text() for tag in article_tags][0]
            article_title = article_body_title[article_links.index(article_url)]
            article_body.append((article_title, article_text.replace('\n', ' ').replace('\xa0', '')))

        self.data['section_tree_url'] = [url for urls in section_tree_url for url in urls]
        self.data['section_title'] = [title for titles in section_title for title in titles]
        self.data['article_links'] = article_links
        self.data['article_link_title'] = article_body_title
        self.data['article_body'] = [body for title, body in article_body]

    def save_to_json(self, filename: str):
        """
        Save the scraped data to a JSON file
        """
        if not os.path.exists('./data'):
            os.makedirs('./data')
        filepath = os.path.join('./data', filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)
