

from lib.classses.UnclaimedBalanceDownloader import UnclaimedBalanceDownloader
from lib.utils.getpath import get_project_root
from lib.classses.UnclaimedBalancesDashboard import UnclaimedBalancesDashboard


if __name__ == "__main__":
    url = "https://www.mof.gov.jm/wp-content/uploads/124-Pages-June-17-2025-.pdf"
    root_path = str(get_project_root())
    pdf_fileName=root_path + "/download/" +url.split("/")[-1]
    output_path = root_path + "/output/unclaimed_balances.csv"
    
    unclaimed_balance = UnclaimedBalanceDownloader(url, pdf_fileName)
    
    unclaimed_balance.download_file()
    customer_data = unclaimed_balance.read_file()
    unclaimed_balance.save_to_csv(customer_data, output_path)
    
    dashboard = UnclaimedBalancesDashboard(output_path, default_page_size=50)
    app = dashboard.app
    server = dashboard.server  # This exposes the Flask server instance

    dashboard.run() 