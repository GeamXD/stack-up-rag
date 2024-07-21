import os
from web_scraper import WebScraper

def check_data_folder():
    """
    Check if the data folder exists and contains a JSON file.
    If not, run the WebScraper class to scrape data and save it to a JSON file.
    """
    data_folder = './data'
    json_file = 'stack-help_data.json'
    json_path = os.path.join(data_folder, json_file)

    # Check if data folder exists
    if not os.path.exists(data_folder):
        print("Data folder not found. Creating folder and running scraper...")
        os.makedirs(data_folder)
        run_scraper(json_path)
    else:
        # Check if JSON file exists in data folder
        if not os.path.exists(json_path):
            print("JSON data file not found. Running scraper...")
            run_scraper(json_path)
        else:
            print("Data folder and JSON file found. No need to run scraper.")

def run_scraper(json_path):
    """
    Run the WebScraper class and save the data to a JSON file.
    """
    scraper = WebScraper('https://stackuphelpcentre.zendesk.com/')
    scraper.scrape()
    scraper.save_to_json(os.path.basename(json_path))
    print(f"Scraped data saved to {json_path}")

if __name__ == '__main__':
    check_data_folder()
