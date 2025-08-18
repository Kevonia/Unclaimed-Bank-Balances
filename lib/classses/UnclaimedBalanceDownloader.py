import requests
from pypdf import PdfReader
import csv
import os
from lib.utils.getpath import check_if_file_exists
from lib.utils.helper import extract_unclaimed_balances


class UnclaimedBalanceDownloader:
    "Class to handle unclaimed balance operations."
    """param url: str - The URL of the file to download. 
       param path: str - The local path to save the downloaded file.
    """
    account_type = ""
    
    def __init__(self, url, path):
        self.url = url
        self.path = path

    def download_file(self):
        """Download the file from the given URL and save it to the specified path."""
        """param url: str - The URL of the file to download.
           param path: str - The local path to save the downloaded file.  """
        """return: None"""
        try:
          
          is_downloaded = check_if_file_exists(self.path)
          if is_downloaded:
              print(f"File already exists at {self.path}")
              return
          else:
              print(f"Downloading file from {self.url} to {self.path}")
          response = requests.get(self.url)
          if response.status_code == 200:
              with open(self.path, 'wb') as file:
                  file.write(response.content)
              print(f"File downloaded successfully to {self.path}")
          else:
              print(
                  f"Failed to download file. Status code: {response.status_code}")
              return
        except requests.exceptions.RequestException as e:
            print(f"Error downloading file: {e}")
            return 
        except IOError as e:
            print(f"Error saving file: {e}")
            return
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return    
              

    def read_file(self) -> list:
        """Read the downloaded file."""
        """param path: str - The local path to the downloaded file."""
        """return: list - A list of lists containing customer name, account number, last activity date, and balance."""
     
        try:
          data = []
          if not check_if_file_exists(self.path):
              print(f"File does not exist at {self.path}")
              return
          reader = PdfReader(self.path)
          number_of_pages = len(reader.pages)
          print(f"Number of pages in the PDF: {number_of_pages}")
          for i in range(number_of_pages):
            print(f"Reading page {i + 1 } of {number_of_pages}")
            page = reader.pages[i]
            text = page.extract_text()
            if not text:
                print(f"No text found on page {i + 1}")
                continue
            if "CURRENT ACCOUNTS (JMD)" in text:
                self.account_type = "Current Accounts"
            elif "SAVINGS ACCOUNTS (JMD)" in text:
                self.account_type = "Savings Accounts"    
                             
            table_data = extract_unclaimed_balances(text, self.account_type),
            for recond in table_data:
              for row in recond:
                data.append(row)
          return data
        except FileNotFoundError:
            print(f"File not found at {self.path}")
            return []
        except Exception as e:
            print(f"Error reading file: {e}")
            return []
        
    def save_to_csv(self, data :list, csv_path :str):
        """Save the extracted data to a CSV file."""
        """param data: list - The data to save to CSV.
           param csv_path: str - The path where the CSV file will be saved.
        """
        try:
        # Create directory if it doesn't exist
          os.makedirs(os.path.dirname(csv_path), exist_ok=True)
              
          with open(csv_path, 'w', newline='') as csvfile:
              writer = csv.writer(csvfile)
              writer.writerow(['Customer Name', 'Account Number', 'Last Activity Date', 'Balance', 'Account Type'])
              writer.writerows(data)
          print(f"Data saved to {csv_path}")
        except IOError as e:
            print(f"Error writing to CSV file: {e}")
        except Exception as e:
            print(f"Error saving to CSV: {e}")
           
    def __str__(self):
        return f"UnclaimedBalance(url={self.url}, path={self.path})"