import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(URL, KEY)

def getAllStocks():
    #Fetches the list of all stocks from the database
    response = supabase.table("stocks").select("*").order("ticker").execute()
    return response.data

def getUserProfile(userID):
    #Fetches a specific player's profile
    try:
        response = supabase.table("profiles").select("*").eq("id", userID).maybe_single().execute()
        return response.data
    except Exception as e:
        print(f"Database Error: {e}")
        return None


def placeBuyOrder(userID, ticker, quantity, price):
    #Calls the Supabase RPC function to process a trade
    try:
        supabase.rpc("execute_buy_order", {
            "p_user_id": userID,
            "p_ticker": ticker,
            "p_quantity": quantity,
            "p_price": price
        }).execute()
        return True, "Trade Successful!"
    except Exception as e:
        return False, str(e)
    
def getUserPortfolio(userID):
    #Fetches the user's current holdings and joins with the stocks table to get live prices for P/L calc
    response = supabase.table('portfolios') \
        .select("ticker, shares_count, avg_price, stocks(name, current_price)") \
        .eq("user_id", userID) \
        .execute()
    return response.data

def placeSellOrder(userID, ticker, quantity, price):
    #Calls another RPC function to process a sale
    try:
        supabase.rpc("execute_sell_order", {
            "p_user_id": userID,
            'p_ticker': ticker,
            "p_quantity": quantity,
            "p_price": price
        }).execute()
        return True, "Sale Successful!"
    except Exception as e: return False, str(e)

def getTransactionHist(userID):
    #Fetches a log of all completed trades
    response = supabase.table("transactions") \
        .select("*") \
        .eq("user_id", userID) \
        .order("created_at", desc=True) \
        .execute()
    return response.data

def getLeaderboard():
    #Fetches top players by total net worth
    response = supabase.table("leaderboard").select("*").limit(10).execute()
    return response.data