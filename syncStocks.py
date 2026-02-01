import os
import financegy
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

#Create Supabase Connection
#TODO: Make DB URL and Key environ variables later
URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(URL, KEY)

def syncMarketData():
    """
    Fetches the latest trading data from the Guyana Stock Exchange 
    and updates the local Supabase 'stocks' table.
    """
    print("Starting Guyana Stock Exchange Market Sync.....")

    # 1. Retrieve the list of all companies/securities currently traded on the GSE
    securities = financegy.get_securities()

    stock_data = []
    
    # 2. Iterate through each security to fetch its specific market performance
    for sec in securities:
        symbol = sec['symbol']
        trade = financegy.get_recent_trade(symbol)

        # Skip logic if no trade data is returned for this ticker
        if trade:
            # 3. Extract 'ltp' (Last Traded Price) - the standard market value
            raw_price = trade.get('ltp')
            
            if raw_price:
                try:
                    # Data Cleaning: GSE prices often contain commas (e.g., "3,500.0").
                    # We strip commas so Postgres 'numeric' type can process it as a float.
                    price = float(str(raw_price).replace(',', ''))

                    # Prepare the object for Supabase upsert
                    stock_data.append({
                        "ticker": symbol,
                        "name": sec.get('name', 'Unknown'),
                        "current_price": price,
                        "last_updated": "now()" # Postgres will interpret this as the current timestamp
                    })
                except ValueError:
                    # Log parsing errors without crashing the entire sync
                    print(f"Could not parse price for {symbol}: {raw_price}")
            else:
                print(f"No price data for {symbol}")

    # 4. Batch update the database
    if stock_data:
        # 'upsert' updates the price if the ticker exists, or inserts it if new
        supabase.table("stocks").upsert(stock_data).execute()
        print(f"Synced {len(stock_data)} securities to the DB")
    else:
        print("No trade data found to sync")

if __name__ == "__main__":
    syncMarketData()