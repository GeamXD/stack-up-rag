from bs4 import BeautifulSoup
import requests

# Fetch the webpage
base_url = 'https://stackuphelpcentre.zendesk.com/'
main_page_response = requests.get(base_url, timeout=5)

# Parse the HTML with BeautifulSoup
main_page_soup = BeautifulSoup(main_page_response.content, 'lxml')

# Extract all <a> tags with the class blocks-item-links
a_tags_main = main_page_soup.select('a.blocks-item-link')

# Store main page links and Title
main_urls = []
main_titles = []

# Iterate through the tags and print href and text
for main_tag in a_tags_main:
    href = base_url + main_tag.get('href')  # Get the href attribute
    text = main_tag.get_text()   # Get the text content
    main_urls.append(href)
    main_titles.append(text.replace('\n', '')) # remove new line characters

# Zip main urls and main title
zipped_main_title_urls = list(zip(main_titles, main_urls))

# Store section tree url and title
section_tree_url = []
section_title = []

# loop through zipped_main_title_urls and get section_title_links
for _, main_url in zipped_main_title_urls:
    section_response = requests.get(main_url, timeout=5) # get the section response per url
    section_soup = BeautifulSoup(section_response.content, 'lxml')
    section_a_tags = section_soup.select('section.section h2 a')
    
    tag_urls = []
    tag_texts = []
    
    for section_a_tag in section_a_tags:
        section_href = base_url[:-1] + section_a_tag.get('href')  # Get the href attribute
        section_text = section_a_tag.get_text()   # Get the text content
        tag_urls.append(section_href)
        tag_texts.append(section_text.replace('\n', ''))
        
    section_tree_url.append(tag_urls)
    section_title.append(tag_texts) # remove new line characters

# zipped section tree url and title
zipped_section_tr_url_title = list(zip(section_title, section_tree_url))

# Match urls with texts for better representation
zipped_section_tr_url_title_clean = [list(zip(zipped_section_tr_url_title[x][0], zipped_section_tr_url_title[x][1])) for x in range(len(zipped_section_tr_url_title))]


# section urls links only
section_url_links = [i for j in section_tree_url for i in j]

article_urls = []
for sec_tr_url in section_url_links:
    sec_tr_response = requests.get(sec_tr_url, timeout=5)
    sec_tr_soup = BeautifulSoup(sec_tr_response.content, 'lxml')
    sec_tr_a_tags = sec_tr_soup.select('a.article-list-link')
    
    article_lnk = []
    for sec_tr_a_tag in sec_tr_a_tags:
        article_href = base_url[:-1] + sec_tr_a_tag.get('href')  # Get the href attribute
        article_lnk.append(article_href)
        
    article_urls.append(article_lnk)


article_urls_only = [i for j in article_urls for i in j]
# Extract section URL links only

text_body = []
# GET ARTICLE TITLE AND ARTICLE CONTENT
for art_url in article_urls_only:
    art_response = requests.get(art_url, timeout=5)
    art_soup = BeautifulSoup(art_response.content, 'lxml')
    art_bdy_tag = art_soup.select('div.article-body')
    art_ttle_tag = art_soup.select('h1.article-title')
    text_body.append((art_ttle_tag[0].get_text().replace('\n', ''), art_bdy_tag[0].get_text().replace('\n', ' ')))
    break




# print(text_body)
