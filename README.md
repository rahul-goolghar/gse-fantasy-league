# Guyana Stock Exchange - Fantasy League (GSE-FL)

**GSE-FL** is an educational investment simulation designed to teach the fundamentals of the Guyana Stock Exchange. Built as a high-contrast, "terminal-style" web application, it allows users to manage a virtual $1M GYD portfolio and compete in a real-time wealth leaderboard.

## 🛠️ The Tech Stack
* **Frontend:** Streamlit with custom CSS injection for a "Dark Terminal" aesthetic.
* **Data Visualization:** Altair (Vega-Lite) configured with **JetBrains Mono** for financial precision.
* **Database:** Supabase (PostgreSQL) for user accounts, portfolio holdings, and real-time leaderboard data.
* **Automation:** GitHub Actions running a daily Python synchronization script to fetch market updates.

## 🚀 Engineering Highlights

### 1. Automated Market Sync Pipeline
The application features a fully automated data pipeline. A dedicated Python script (`syncStocks.py`) is triggered every 24 hours via GitHub Actions. This ensures that stock prices for companies like BTI, DIH, and DTC remain accurate to the latest market close without manual intervention.

### 2. High-Precision UI/UX
To move away from the standard "web app" feel, I implemented a custom CSS layer that enforces a unified design language:
* **Typography:** Inter for UI headers and JetBrains Mono for all numeric financial data.
* **Theming:** A signature neon green (**#00ff88**) accent used across metrics, charts, and interactive elements.
* **Responsive Tables:** Centered, high-contrast tables designed for quick data scanning.

### 3. Fantasy League Mechanics
* **Starting Capital:** Each new user is initialized with a virtual balance of $1,000,000.00 GYD.
* **Real-World Data:** Trading reflects actual GASCI price movements, providing a risk-free environment for students to learn market dynamics.
* **Live Rankings:** A global leaderboard tracks total net worth (Cash + Assets) across the entire user base.


## 📂 Project Structure
```text
├── .github/workflows/
│   └── sync_stocks.yml    # Automation for daily price updates
├── app.py                 # Main Streamlit application
├── database.py            # Supabase connection & CRUD logic
├── syncStocks.py          # Independent script for market data sync
├── styles.css             # Custom terminal styling
└── requirements.txt       # Project dependencies
```

## ⚙️ Setup & Installation

Follow these steps to set up the development environment on your local machine:

### 1. Clone the Repository
```bash
git clone https://github.com/rahul-goolghar/gse-fantasy-league.git
cd gse-fantasy-league
```
### 2. Setup Virtual Environment
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a .env file in the root and add your Supabase credentials
```base
SUPABASE_URL=your_project_url_here
SUPABASE_KEY=your_api_key_here
```

### 5. Launch the Application
```bash
streamlit run app.py
```
