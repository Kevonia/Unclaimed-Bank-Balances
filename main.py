from lib.classses.UnclaimedBalanceDownloader import UnclaimedBalanceDownloader
from lib.utils.getpath import get_project_root
from lib.classses.UnclaimedBalancesDashboard import UnclaimedBalancesDashboard

# Initialize your Dash app at module level (not inside __main__)
url = "https://www.mof.gov.jm/wp-content/uploads/124-Pages-June-17-2025-.pdf"
root_path = str(get_project_root())
pdf_fileName = root_path + "/download/" + url.split("/")[-1]
output_path = root_path + "/output/unclaimed_balances.csv"

# Initialize dashboard
dashboard = UnclaimedBalancesDashboard(output_path, default_page_size=50, url=url)
app = dashboard.app
server = dashboard.server  # This is what Gunicorn needs to access

# Only run directly when executed (not when imported)
if __name__ == "__main__":
    dashboard.run()