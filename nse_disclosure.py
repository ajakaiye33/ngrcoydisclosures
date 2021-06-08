import pandas as pd
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
import configparser
import requests.exceptions as requests_exception


#  get resource
parser = configparser.ConfigParser(interpolation=None)
parser.read("nseurl.conf")
url = parser.get("nseapi", 'url')

output_data = "./docs/coy_disclosures.json"


def corporate_disclosure(url=url):
    """
    Issue a GET request and scrape data from xml
    """
    # collect data
    url = str(url)

    nse_company_disclosures = []
    try:
        res = requests.get(url)
        resp = res.text
    except requests_exception.MissingSchema:
        print(f"resource locator not available at the moment")
    except requests_exception.ConnectionError:
        print(f"Could not connect to resource")
    soup = BeautifulSoup(resp, 'xml')
    child = soup.find_all('entry')
    number_row = len(child)
    print(f"{number_row}, rows of data received")
    for siblings in child:
        grand_children = {}
        grand_children['updated'] = siblings.find('updated').get_text()
        grand_children['headline'] = siblings.find('Description').get_text()
        grand_children['location'] = siblings.find('Url').get_text()
        grand_children['news_class'] = siblings.find('Type_of_Submission').get_text()
        grand_children['company_name'] = siblings.find('CompanyName').get_text()
        grand_children['company_symbol'] = siblings.find('CompanySymbol').get_text()
        grand_children['date_modified'] = siblings.find('Modified').get_text()
        grand_children['date_created'] = siblings.find('Created').get_text()
        nse_company_disclosures.append(grand_children)
    return nse_company_disclosures


data = corporate_disclosure()

# save data to json


def tojson():
    try:
        with open(output_data, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as err:
        print(err)

# save insider dealings notifications to csv


def insider_deals():
    df = pd.DataFrame(data)
    insider_dealings = df[df['news_class'] == "Directors Dealings"]
    insider_dealings.to_csv("./docs/insider-dealings.csv", index=False)


# save financial statements notifications to csv
def fin_statement():
    df = pd.DataFrame(data)
    fin_statements = df[df['news_class'] == "Financial Statements"]
    fin_statements.to_csv("./docs/financial-statement.csv", index=False)


def main():
    tojson()
    insider_deals()
    fin_statement()


if __name__ == "__main__":
    main()
