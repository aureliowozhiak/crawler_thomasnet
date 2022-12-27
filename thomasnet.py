import requests
import pandas as pd
from lxml import etree
from bs4 import BeautifulSoup

class Scraper:
    """A class for scraping information from thomasnet website"""

    def __init__(self, url = "https://www.thomasnet.com/nsearch.html?act=C&cov=NA&heading=30772305&navsec=modify&what=Food+Products&which=prod"):
        """
        Initialize the Scraper instance.
        
        Parameters:
            url (str): The URL of the website to scrape.
        """
        self.url = url

    def get_company_links(self):
        """
        Retrieve the URLs of the company pages on the website.
        
        Returns:
            List[str]: A list of URLs for the company pages.
        """
        
        # Make a request to the website and retrieve the HTML content
        response = requests.get(self.url)
        html = response.content

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        # Extract the URLs of the company pages from the HTML
        company_links = []
        for title in soup.find_all("h2", class_="profile-card__title"):
            company_links.append(title.find_all("a")[0]["href"])

        return company_links

    def get_info_from_link(self, link):
        """
        Retrieve information about a company from its page on the website.
        
        Parameters:
            link (str): The URL of the company's page.
            
        Returns:
            Dict: A dictionary containing the company's name, address, website, business description, and phone number.
        """
        # Construct the full URL of the company's page
        company_url = "https://www.thomasnet.com" + link
        
        # Make a request to the company's page and retrieve the HTML content
        company_response = requests.get(company_url)
        company_html = company_response.content

        # Parse the HTML content using BeautifulSoup
        company_soup = BeautifulSoup(company_html, "html.parser")

        
        # Extract the company's name, address, and website from the HTML
        name = company_soup.find("h1", class_="copro-supplier-name").text.replace("\n", "")
        address = company_soup.find("span", class_="copro-address-line").text.replace("\n", "")
        website = company_soup.find("a", class_="text")['href'].replace("\n", "")

        
        # Extract the company's business description from the HTML
        business_description = company_soup.find("div", id="copro_pdm")
        if business_description is not None:
            business_description = business_description.find("p").text


        # Extract the company's phone number from the HTML using lxml and XPath
        phone_number = etree.HTML(str(company_soup)).xpath('//*[@id="copro_naft"]/div[1]/div/p[2]/span[2]')
        if phone_number:
            phone_number = phone_number[0].text
        else:
            phone_number = None

        return {'name':name, 
                'address':address,
                'website':website,
                'thomasnet_company_url':company_url,
                'business_description':business_description,
                'phone_number': phone_number}

    def consolidating_data(self):
        """
        Retrieve information about all the companies on the website and consolidate it into a DataFrame.
        
        Returns:
            pd.DataFrame: A DataFrame containing the name, address, website, business description, and phone number of all the companies.
        """
        # Get the URLs of all the company pages on the website
        company_links = self.get_company_links()

        # Retrieve the information about each company and store it in a list
        data = []
        for link in company_links:
            data.append(self.get_info_from_link(link))

        # Convert the list of company information into a DataFrame
        return pd.DataFrame(data)
