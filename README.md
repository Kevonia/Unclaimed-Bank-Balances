# Unclaimed Balances Dashboard

This project provides a complete pipeline to **download**, **process**, and **analyze** unclaimed balance data from the Jamaican Ministry of Finance. It automatically downloads the official PDF, extracts customer records, saves them as a CSV file, and launches an interactive **Plotly Dash** dashboard for exploration.  

---

## Features
- 📥 **Automated PDF Download** – Fetches the unclaimed balances report directly from the Ministry of Finance website.  
- 📑 **Data Extraction** – Parses the PDF and extracts tabular customer data.  
- 💾 **CSV Export** – Saves the structured dataset for future use.  
- 📊 **Interactive Dashboard** – Visualizes balances with filtering, sorting, and charts (using Plotly + Dash).  
- ⚡ **Flask Server Ready** – Exposes a Flask server instance for deployment (e.g., Gunicorn, Waitress, or Docker).  

---

## Project Structure
```
.
├── lib/
│   ├── classes/
│   │   ├── UnclaimedBalanceDownloader.py   # Handles download, parsing, and CSV export
│   │   └── UnclaimedBalancesDashboard.py   # Creates Plotly/Dash dashboard
│   └── utils/
│       └── getpath.py                      # Utility for project root resolution
        └── helper.py                       # Utility for extract info from string
├── download/                               # Stores downloaded PDF files
├── output/                                 # Stores processed CSV files
├── main.py                                 # Entry point (pipeline + dashboard runner)
└── README.md
```

---

## Requirements
- Python **3.10+**  
- Libraries:  
  ```bash
  pip install pandas numpy plotly dash waitress requests PyPDF2
  ```

---

## Usage

1. Clone this repository:
   ```bash
   git clone https://github.com/Kevonia/Unclaimed-Bank-Balances
   cd unclaimed-balances-dashboard
   ```

2. Run the script:
   ```bash
   python main.py
   ```

3. The script will:
   - Download the latest unclaimed balances report (PDF).  
   - Extract the data into `output/unclaimed_balances.csv`.  
   - Launch the interactive dashboard at:  
     ```
     http://127.0.0.1:8080
     ```

---

## Configuration
- **Default URL** – Set in `main.py`:
  ```python
  url = "https://www.mof.gov.jm/wp-content/uploads/124-Pages-June-17-2025-.pdf"
  ```
- **Output CSV Path** – Controlled by:
  ```python
  output_path = root_path + "/output/unclaimed_balances.csv"
  ```
- **Dashboard Page Size** – Change default page size in:
  ```python
  dashboard = UnclaimedBalancesDashboard(output_path, default_page_size=50)
  ```

---

## Deployment
Since the project exposes the Flask server instance:
```python
server = dashboard.server
```
You can deploy with **Waitress**, **Gunicorn**, or **Docker** for production environments.

Example (Gunicorn):
```bash
gunicorn -w 4 -b 0.0.0.0:8080 main:server
```

---

## License
This project is for **educational and analytical purposes only**. Data belongs to the **Ministry of Finance & the Public Service (Jamaica)**.  
