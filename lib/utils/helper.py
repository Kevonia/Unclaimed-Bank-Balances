import re
from  lib.constants.bank_list import jamaican_banks  

def extract_unclaimed_balances(text :str,account_type: str,bank_name:str,published_date:str) -> list:
      """Extract unclaimed balances from the given text."""
      """ param text: str - The text to extract unclaimed balances from."""
      """ param account_type: str - The type of account (e.g., 'Savings', 'Checking')."""
      """ param bank_name: str - The name of the bank."""
      """Returns a list of lists containing customer name, transit/account number, last activity date, and balance."""
  
      # This pattern matches:
      # 1. Customer name (may contain spaces, dots, and special characters)
      # 2. Transit/Account number (digits and maybe letters)
      # 3. Date in dd-mmm-yyyy format
      # 4. Balance with optional comma as thousand separator
      
      pattern = r'^([A-Z][A-Za-z\s\.,&\'-]+)\s+(\d+[A-Za-z]*\s+\d+)\s+(\d{1,2}-[A-Za-z]{3}-\d{4})\s+([\d,]+\.\d{2})\s*$'
      
      matches = re.finditer(pattern, text, re.MULTILINE)
      
      results = []
      for match in matches:
          customer_name = match.group(1).strip()
          account_number = match.group(2).strip()
          last_activity_date = match.group(3).strip()
          balance = match.group(4).strip()
          account_type = account_type
          bank_name=bank_name
          published_date = published_date
          results.append([customer_name, account_number, last_activity_date, balance,account_type,bank_name,published_date])
      
      return results
  
  
def extract_name_date(name :str) -> list:
      """Extract name and date from the given text."""
      """ param name: (str) - The text to extract name and date from."""
      """Returns the date in the format 'Month-Day-Year'."""
      pattern = r'(\w+-\d{1,2}-\d{4})'

      match = re.search(pattern, name)
      if match:
          date_string = match.group(1)
          return date_string
  
  
def search_jamaican_banks(search_term):
    """
    Search Jamaican banks dictionary with partial matching.
    Extracts bank codes from the search term and ignores additional text.
    param: search_term (str): The term to search for (case-insensitive)
    Returns:
        dict: Dictionary of matching banks {code: full_name} or empty dict if no matches
    """
    search_term = search_term.lower().strip()
    matches = {}
    
    # First, try to extract bank codes from the search term
    for bank_code in jamaican_banks.keys():
        # Check if any bank code appears in the search term (case-insensitive)
        if bank_code.lower() in search_term:
            matches[bank_code] = jamaican_banks[bank_code]
    
    # If no bank codes found, try partial matching with bank names
    if not matches:
        for code, full_name in jamaican_banks.items():
            # Check if search term contains any part of bank name or vice versa
            if (any(word in search_term for word in full_name.lower().split()) or
                any(word in full_name.lower() for word in search_term.split())):
                matches[code] = full_name
    
    return matches