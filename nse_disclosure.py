#created by Hedgar 26/09/2021

import json
import configparser
import pandas as pd
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Union

class CorporateDisclosure:
    def __init__(self):
        self.config = self.read_config("nseurl.conf")
        self.url = self.config.get("nseapi", 'url')
        self.output_data = "./docs/coy_disclosures.json"
        self.data = self.fetch_data()

    @staticmethod
    def read_config(file_path: str) -> configparser.ConfigParser:
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(file_path)
        return parser

    def fetch_data(self) -> List[Dict[str, Union[str, int]]]:
        try:
            res = requests.get(self.url)
            res.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to fetch data: {e}")
            return []

        soup = BeautifulSoup(res.text, 'xml')
        entries = soup.find_all('entry')
        print(f"{len(entries)}, rows of data received")

        return [{
            'updated': entry.find('updated').get_text(),
            'headline': entry.find('Description').get_text(),
            'location': entry.find('Url').get_text(),
            'news_class': entry.find('Type_of_Submission').get_text(),
            'company_name': entry.find('CompanyName').get_text(),
            'company_symbol': entry.find('CompanySymbol').get_text(),
            'date_modified': entry.find('Modified').get_text(),
            'date_created': entry.find('Created').get_text()
        } for entry in entries]

    def to_json(self) -> None:
        try:
            with open(self.output_data, "w") as f:
                json.dump(self.data, f, indent=4)
        except Exception as err:
            print(f"Failed to save to JSON: {err}")

    def save_filtered_data(self, key: str, value: str, file_name: str) -> None:
        df = pd.DataFrame(self.data)
        filtered_data = df[df[key] == value]
        filtered_data.to_csv(f"./docs/{file_name}.csv", index=False)

    def main(self) -> None:
        self.to_json()
        self.save_filtered_data('news_class', "Directors Dealings", "insider-dealings")
        self.save_filtered_data('news_class', "Financial Statements", "financial-statement")


if __name__ == "__main__":
    corp_disclosure = CorporateDisclosure()
    corp_disclosure.main()
