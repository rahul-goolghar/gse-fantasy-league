import streamlit as st
import pandas as pd
import pytz
import altair as alt
from database import (
    getAllStocks, placeBuyOrder, getUserProfile, 
    getUserPortfolio, placeSellOrder, getTransactionHist, 
    supabase, getLeaderboard
)
#DEFINE LOCAL TIMEZONE
guyanaTZ = pytz.timezone('America/Guyana')

# PAGE CONFIGURATION
st.set_page_config(page_title="GSE Fantasy League", layout="wide")

# CUSTOM CSS STYLING
def localCSS(fileName):
    with open(fileName) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

localCSS("styles.css")

# SIDEBAR AUTHENTICATION LOGIC
def loginSidebar():
    st.sidebar.title("👤 Account")
    try:
        userResponse = supabase.auth.get_user()
        user = userResponse.user
    except:
        user = None

    if not user:
        tab1, tab2 = st.sidebar.tabs(["Login", "Sign Up"])

        with tab1:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login", use_container_width=True):
                try:
                    supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.rerun()
                except Exception as e:
                    st.sidebar.error(f"Login failed: {e}")

        with tab2:
            newEmail = st.text_input("Email", key="reg_email")
            newPass = st.text_input("Password", type="password", key="reg_pass")
            newUser = st.text_input("Username", key="reg_user") 

            if st.button("Create Account", use_container_width=True):
                try:
                    supabase.auth.sign_up({
                        "email": newEmail, 
                        "password": newPass,
                        "options": {"data": {"username": newUser}}
                    })
                    st.success("Account created! Log in to start.")
                except Exception as e:
                    st.error(f"Sign up failed: {e}")
        return None
    else:
        st.sidebar.write(f"Logged In As: **{user.email}**")
        if st.sidebar.button("Logout", use_container_width=True):
            supabase.auth.sign_out()
            st.rerun()
        return user.id

# SHARED COMPONENT: ABOUT & CREDITS
def renderAboutSection():
    st.markdown("""
    ### 📖 Project Overview: A Minimal Trading Experience
    **How the "Fantasy League" Works:**
    * **Virtual Starting Capital:** Every new user starts with a fixed balance of $1,000,000.00 GYD in virtual "play money".
    * **Live Market Pulse:** The app fetches real-time (or near real-time) prices for Guyanese companies like BTI, DIH, and DTC, allowing users to trade against actual market trends.
    * **Simplified Execution:** To keep the MVP accessible for students, the simulation ignores complex market factors like bid/ask spreads, brokerage commissions, or dividend yields.
    * **Instant Settlement:** Transactions are processed immediately against the user's virtual cash balance, providing instant feedback on portfolio performance.
    * **Competitive Leaderboard:** Users are ranked based on their Total Net Worth (Cash + Current Market Value of Holdings), creating a gamified environment for learning.

    **Core Engineering Features:**
    * **Automated Data Pipeline:** A Python-based sync script fetches live prices from FinanceGY and updates the Supabase backend via GitHub Actions.
    * **Relational Database Architecture:** Uses Supabase (PostgreSQL) with **Row Level Security (RLS)** to ensure data privacy across multiple users.
    * **Transaction Integrity:** Custom SQL functions (RPCs) handle buy/sell logic to prevent "race conditions" or insufficient fund errors.
                
    **Market Data & Update Frequency**
    * **Update Frequency:** Stock prices are refreshed once every 24 hours to reflect the official closing prices from the Guyana Stock Exchange.
    * **Leaderboard Impact:** Because prices update daily, your Total Net Worth and Leaderboard Rank are recalculated every time the market "closes" for the day.
    * **Profit & Loss (P/L) Logic:** he P/L ($) and P/L (%) columns in your portfolio are dynamic; they compare your original **Average Purchase Price** against the **latest daily update**.
    * **Static vs Active:** During the trading day, your P/L will remain static until the next data sync, encouraging users to focus on long-term value rather than intra-day volatility.
    
    ### 🎖️ Credits & Tech Stack
    * **Developer:** [Rahul Goolghar](https://www.linkedin.com/in/rahul-goolghar-6a9b122b0/)
    * **Data Source:** [FinanceGY](https://github.com/xbze3/financegy) Developed by [Ezra Minty](https://www.linkedin.com/in/ezra-minty/)
    * **Frontend:** [Streamlit](https://docs.streamlit.io/)
    * **Backend & Authentication:** [Supabase](https://supabase.com/)
    """)

# INITIALIZE AUTH
USER_ID = loginSidebar()

# MAIN CONTENT ROUTER
if not USER_ID:
    # --- LANDING PAGE (VISITOR STATE) ---
    st.title("Guyana Stock Exchange: Fantasy League (MVP)")
    
    land_tab1, land_tab2 = st.tabs(["🏠 Home", "ℹ️ About the Project"])
    
    with land_tab1:
        st.markdown("""
        ### Master the Market with $1,000,000 Virtual Capital
        Experience the Guyanese stock market without financial risk. 
        * **Live Market Sync:** Trade with the latest GSE prices.
        * **Portfolio Tracking:** View your gains, losses, and average costs.
        * **Compete:** See where you rank on the global leaderboard.
        
        **Please use the sidebar to Login or Sign Up to unlock the dashboard.**
        """)
        st.info("**Ready to Trade?** Sign up now to receive your virtual $1,000,000 GYD immediately.")
            
    with land_tab2:
        renderAboutSection()

else:
    # --- DASHBOARD (LOGGED IN STATE) ---
    st.title("Guyana Stock Exchange: Fantasy League")
    
    choice = st.segmented_control(
        "Navigation", 
        options=["📈 Market Prices", "📁 My Portfolio", "🏆 Leaderboard", "ℹ️ About"],
        default="📈 Market Prices"
    )
    st.divider()

    # --- MARKET PRICES ---
    if choice == "📈 Market Prices":
        st.subheader("Current Market Prices")
        stocks = getAllStocks()

        if stocks:
            df = pd.DataFrame(stocks)
            df['last_updated'] = pd.to_datetime(df['last_updated']) \
                .dt.tz_convert(guyanaTZ) \
                .dt.strftime('%b %d, %I:%M %p')
            df_display = df[['ticker', 'name', 'current_price', 'last_updated']]
            st.dataframe(
                df_display,
                column_config={
                    "ticker": st.column_config.TextColumn("Ticker", width="small"),
                    "name": st.column_config.TextColumn("Company Name", width="medium"),
                    "current_price": st.column_config.NumberColumn("Price (GYD)", format="$%d"),
                    "daily_change": st.column_config.NumberColumn("Change (%)", format="%.2f%%"),
                },
                hide_index=True,
                use_container_width=True
            )
            #st.table(df_display)
            
            st.divider()
            st.subheader("Place a Buy Order")
            col1, col2, col3 = st.columns(3)

            with col1:
                selectedTicker = st.selectbox("Select Ticker", df['ticker'].unique())
            
            with col2:
                qty = st.number_input("Quantity to Buy", min_value=1, step=1, value=1)

            with col3:
                currentPrice = df[df['ticker'] == selectedTicker]['current_price'].values[0]
                totalCost = qty * currentPrice
                #st.metric("Current Price", f"${currentPrice:,.2f} GYD")
                st.metric("Total Transaction Cost", f"${totalCost:,.2f} GYD")

            #st.write(f"Total Transaction Cost: **${totalCost:,.2f} GYD**")

            if st.button("Confirm Purchase", type="primary"):
                success, message = placeBuyOrder(USER_ID, selectedTicker, qty, currentPrice)
                if success:
                    st.success(message)
                    st.balloons()
                else:
                    st.error(f"Trade Failed: {message}")
        else:
            st.write("No Stock Data Found.")

    # --- PORTFOLIO ---
    elif choice == "📁 My Portfolio":
        st.subheader("My Investment Portfolio")
        profile = getUserProfile(USER_ID)
        
        if profile:
            holdings = getUserPortfolio(USER_ID)
            colP1, colP2 = st.columns(2)
            with colP1:
                st.metric("Available Cash", f"${profile['cash_balance']:,.2f} GYD")

            if holdings:
                portfolioList = []
                totalStockVal = 0
                for item in holdings:
                    currentVal = item['shares_count'] * item['stocks']['current_price']
                    totalStockVal += currentVal
                    costBasis = item['shares_count'] * item['avg_price']
                    plAmount = currentVal - costBasis
                    plPercent = (plAmount / costBasis) * 100 if costBasis != 0 else 0

                    # These keys MUST match what the Altair Chart looks for
                    portfolioList.append({
                        "Ticker": item['ticker'],
                        "Name": item['stocks']['name'],
                        "Shares": item['shares_count'],
                        "Average Price": f"${item['avg_price']:,.2f}",
                        "Current Price": f"${item['stocks']['current_price']:,.2f}",
                        "Total Value": f"${currentVal:,.2f}", # Altair will clean this string
                        "P/L ($)": f"${plAmount:,.2f}",
                        "P/L (%)": f"{plPercent:.2f}%" 
                    })

                with colP2:
                    st.metric("Total Stock Value", f"${totalStockVal:,.2f} GYD")

                st.write("### Your Holdings")
                df_holdings = pd.DataFrame(portfolioList)

                # Use st.dataframe with column_config for a professional, responsive look
                st.dataframe(
                    df_holdings,
                    column_config={
                        "Ticker": st.column_config.TextColumn("Ticker", width="small"),
                        "Name": st.column_config.TextColumn("Name", width="medium"),
                        "Shares": st.column_config.NumberColumn("Shares"),
                        "Average Price": st.column_config.TextColumn("Avg Price"),
                        "Current Price": st.column_config.TextColumn("Current"),
                        "Total Value": st.column_config.TextColumn("Value"),
                        "P/L ($)": st.column_config.TextColumn("P/L ($)"),
                        "P/L (%)": st.column_config.TextColumn("P/L (%)"),
                    },
                    hide_index=True,
                    use_container_width=True
                )
                #st.table(portfolioList)

                # --- DISTRIBUTION CHART ---
                st.write("### Portfolio Breakdown")
                dfPie = pd.DataFrame(portfolioList)

                if not dfPie.empty:
                    # Clean the currency string for calculation
                    dfPie['Value_Num'] = (
                        dfPie['Total Value']
                        .astype(str)
                        .str.replace(r'[\$,]| GYD', '', regex=True)
                        .astype(float)
                    )

                    chartP = alt.Chart(dfPie).mark_bar(
                        color='#00ff88', 
                        cornerRadiusTopLeft=4, 
                        cornerRadiusTopRight=4
                    ).encode(
                        # These now match your dictionary keys exactly
                        x=alt.X('Ticker:N', title='STOCK TICKER'),
                        y=alt.Y('Value_Num:Q', title='MARKET VALUE (GYD)'),
                        tooltip=['Ticker:N', 'Total Value:N']
                    ).properties(
                        width='container',
                        height=400
                    ).configure_axis(
                        titleFont='Inter',
                        titleFontSize=20,
                        titleFontWeight=800,
                        titleColor='#8b949e',
                        labelFont='JetBrains Mono',
                        labelFontSize=15,
                        labelColor='#c9d1d9'
                    ).configure_view(strokeWidth=0)

                    st.altair_chart(chartP, use_container_width=True)
                else:
                    st.info("No holdings found to display in the chart.")

                #st.bar_chart(data=dfPie, x='ticker', y='value', color="#00ff88")

                # SELLING LOGIC
                st.divider()
                st.subheader("Liquidate Holdings")
                ownedTickers = [item['ticker'] for item in holdings]
                sellTicker = st.selectbox("Select Stock to Sell", ownedTickers)

                selectedHolding = next(item for item in holdings if item['ticker'] == sellTicker)
                maxQty = selectedHolding['shares_count']
                currentMarketPrice = selectedHolding['stocks']['current_price']

                colS1, colS2 = st.columns(2)
                with colS1:
                    sellQty = st.number_input("Quantity to Sell", min_value=1, max_value=maxQty, value=1)
                with colS2:
                    st.metric("Expected Revenue", f"${(sellQty * currentMarketPrice):,.2f} GYD")

                if st.button("Confirm Sale", type="secondary"):
                    success, message = placeSellOrder(USER_ID, sellTicker, sellQty, currentMarketPrice)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(f"Sale Failed: {message}")
            else:
                st.info("You do not own any stocks yet.")

            # TRANSACTION HISTORY
            st.divider()
            st.subheader("Transaction History")
            history = getTransactionHist(USER_ID)
            if history:
                dfHistory = pd.DataFrame(history)
                dfHistory['created_at'] = pd.to_datetime(dfHistory['created_at']) \
                    .dt.tz_convert(guyanaTZ) \
                    .dt.strftime('%b %d, %I:%M %p')
                dfHistory = dfHistory[['created_at', 'type', 'ticker', 'quantity', 'price', 'total_value']]
                st.dataframe(
                    dfHistory,
                    column_config={
                        "timestamp": st.column_config.DatetimeColumn("Date & Time", format="D MMM, h:mm a"),
                        "ticker": st.column_config.TextColumn("Ticker"),
                        "type": st.column_config.TextColumn("Action"), # Buy/Sell
                        "shares": st.column_config.NumberColumn("Shares"),
                        "price_at_time": st.column_config.NumberColumn("Price", format="$%.2f"),
                        "total_cost": st.column_config.NumberColumn("Total", format="$%.2f"),
                    },
                    hide_index=True,
                    use_container_width=True
                )
                #st.table(dfHistory)
        else:
            st.warning("Profile could not be loaded.")

    # --- LEADERBOARD ---
    elif choice == "🏆 Leaderboard":
        st.subheader("Global Rankings")
        rankings = getLeaderboard()
        if rankings:
            dfLeaderboard = pd.DataFrame(rankings)
            dfLeaderboard.index = dfLeaderboard.index + 1
            dfLeaderboard.index.name = "Rank"
            dfLeaderboard['total_net_worth'] = dfLeaderboard['total_net_worth'].apply(lambda x: f"${x:,.2f} GYD")
            display_cols = ["username", "total_net_worth"]

            # Use the column_config to ensure the currency looks professional
            st.dataframe(
                dfLeaderboard[display_cols], # Pass only the selected columns here
                column_config={
                    "Trader": st.column_config.TextColumn("Trader", width="medium"),
                    "Net Worth (GYD)": st.column_config.NumberColumn("Net Worth", format="$%d")
                },
                hide_index=False,
                use_container_width=True
            )
            #st.table(dfLeaderboard[['username', 'total_net_worth']])

            st.write("### Wealth Distribution")

            # We use .strip() to handle any accidental leading/trailing spaces
            dfLeaderboard['net_worth_numeric'] = (
                dfLeaderboard['total_net_worth']
                .str.replace(r'[\$,]| GYD', '', regex=True)
                .astype(float)
            )

            # Create the Leaderboard Altair Chart
            chartLB = alt.Chart(dfLeaderboard.head(5)).mark_bar(
                color='#00ff88', 
                cornerRadiusTopLeft=4, 
                cornerRadiusTopRight=4
            ).encode(
                x=alt.X('username:N', title='INVESTOR'),
                y=alt.Y('net_worth_numeric:Q', title='NET WORTH (GYD)'),
                tooltip=['username', 'total_net_worth']
            ).properties(
                width='container',
                height=400
            ).configure_axis(
                titleFont='Inter',
                titleFontSize=20,
                titleFontWeight=800,
                titleColor='#8b949e',
                labelFont='JetBrains Mono',
                labelFontSize=15,
                labelColor='#c9d1d9'
            ).configure_view(strokeWidth=0)

            st.altair_chart(chartLB, use_container_width=True)
            #st.bar_chart(data=dfLeaderboard.head(5), x="username", y="stock_value", color="#00ff88")
        else:
            st.info("The leaderboard is currently empty.")

    # --- ABOUT ---
    elif choice == "ℹ️ About":
        renderAboutSection()