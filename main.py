import os 
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings("ignore")


tickers = {"HYBE": "352820.KS",
    "JYP": "035900.KQ",
    "YG": "122870.KQ",}
# Mapping readable company names to official Yahoo Finance ticker symbols

# function to bundle all the data downloading 
def fetch_stock_data():
    print("Fetching stock data from Yahoo Finance")
    print()

    data = yf.download(list(tickers.values()), start = "2023-01-01", progress = False)
    # yfinance requires a list of ticker strings rather than a dictionary

    data = data.dropna()
    # Handles missing values (drops rows where markets were closed or data is missing)
    # to prevent calculation errors later

    if data.empty:
        print("Could not download stock data. Check your internet connection and try again.")
        raise SystemExit
    # yfinance doesn't raise an error when the network is down, it just returns
    # an empty table, so I checked for that and exit the program instead of crashing

    code_to_name = {}

    for name, code in tickers.items():
        code_to_name[code] = name
    # Swap dictionary keys/values so columns display agency names instead of ticker codes

    data = data.rename(columns=code_to_name)
    


    print()
    print("Data preview (First 5 rows):")
    print(data.head())

    return data


def calculate_metrics(data):
    print()
    print("Calculating daily percentage returns and rolling volatility")

    close_prices = data['Close']

    daily_returns = close_prices.pct_change() * 100
    
    rolling_volatility = close_prices.pct_change().rolling(window=20).std() * 100
    # Measures how wildly prices bounced around over the past month (20 days) using standard deviation
        
    print()
    print("Daily Returns Preview (First 5 rows):")
    print(daily_returns.dropna().head())
    # used dropna to remove all missing data
   
    print() 
    print("Rolling 20-Day Volatility Preview (First 5 rows):")
    print(rolling_volatility.dropna().head())
    # used dropna because rows 1-19 would print NaN because rolling volatility needs a 20-day
    # window of data to calculate standard deviation. 

    return daily_returns, rolling_volatility


def get_event_window(df, event_date, window_days=15):
    # Extracts stock data in a 30-day window (+/- window_days) around a specific comeback date.

    print()
    print(f"Extracting event window around comeback date: {event_date}")
    
    target_date = pd.to_datetime(event_date)
    
    start_window = target_date - pd.Timedelta(days=window_days)
    end_window = target_date + pd.Timedelta(days=window_days)
    # pandas timedelta helps you add and subtract dates (if not for this you would be 
    # subtracting 15 days from May 15 which does not make sense)


    window_data = df.loc[start_window:end_window]
    # Slice using data labels to isolate the event window

    return window_data



def plot_event_window(window_data, event_date):
    plt.figure(figsize=(10, 5))

    for column in window_data.columns:
        plt.plot(window_data.index, window_data[column], marker='o', label=column)
        
    plt.axvline(pd.to_datetime(event_date), color='red', linestyle='--', label='Comeback Date')
    
    plt.title(f"K-Pop Stock Reaction Around Comeback: {event_date}", fontsize=14)
    
    plt.xlabel("Date", fontsize=12)
    
    plt.ylabel("Daily Return (%)", fontsize=12)
    
    plt.axhline(0, color='gray', linestyle='-', linewidth=0.8)
    # draws a gray line at y=0 so I can easily see positive vs. negative returns

    plt.legend()
        
    
    plt.grid(True, linestyle=':', alpha=0.6)
    
    plt.xticks(rotation=45)
    
    plt.tight_layout()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Finds the exact folder where this code lives so the chart saves 
    # in the right spot, no matter where the user's terminal is opened from

    output_dir = os.path.join(script_dir, "output")
    
    
    os.makedirs(output_dir, exist_ok=True)
    # creates the output folder if it doesn't exist yet (error handling)
    # and exist_ok=True ensures Python won't crash or throw an error if the folder is already there

    file_path = os.path.join(output_dir, f"comeback_{event_date}.png")

    plt.savefig(file_path)

    print(f"Chart saved as: output/comeback_{event_date}.png")
    
    plt.show()


def analyze_comeback_volatility(volatility_df, event_date, window_days=15):
   print()
   print(f"--- Comeback Volatility Impact Analysis ({event_date}) ---")
    
   vol_slice = get_event_window(volatility_df, event_date, window_days)
    
   if len(vol_slice) == 0:
    print(f"No volatility data found for {event_date}.")
    return

    
   window_avg = vol_slice.mean()
   # Calculate average volatility during the comeback window
   
    

   baseline_avg = volatility_df.mean()
   # Calculate average baseline volatility across all data from 2023 to today
    

   comparison_df = pd.DataFrame({"Comeback Window Volatility (%)": window_avg,
        "Baseline Average Volatility (%)": baseline_avg,
    })
    

   comparison_df["Volatility Spike (%)"] = (
      (comparison_df["Comeback Window Volatility (%)"] - comparison_df["Baseline Average Volatility (%)"]) 
      / comparison_df["Baseline Average Volatility (%)"]
    ) * 100
   # Calculate the percentage difference to see how much wilder it got
   # This formula calculates the percentage increase (or decrease) between
   # the comeback window volatility and the normal baseline volatility.
   # if positive --> agency's stock was __% higher than its average behavior
   # if negative --> agency's stock became less volatile during event window
    
   print(comparison_df.round(2))
   print()
   print("(If Volatility Spike is positive, the stock was wilder during the comeback than usual!)")

   #Interpretation of results
   print()
   print("--- Key Takeaways ---")
   print()
   for ticker, row in comparison_df.iterrows():
    spike = row["Volatility Spike (%)"]
    baseline = row["Baseline Average Volatility (%)"]
    window_val = row["Comeback Window Volatility (%)"]

    if pd.isna(spike):
        print(f"{ticker}: Not enough data yet to measure volatility (needs 20 trading days of history).\n")
    elif spike > 0:
        print(f"{ticker}: Saw a {spike:.1f}% volatility spike.")
        print(f"  -> Translation: Instead of its usual calm daily price swings (~{baseline:.1f}%),")
        print(f"     its daily movements jumped to ~{window_val:.1f}% as the market reacted to the comeback hype.\n")
    else:
        print(f"{ticker}: Remained calm, dropping by {abs(spike):.1f}% compared to normal baseline behavior.\n")

    


if __name__ == "__main__":
  df = fetch_stock_data()

  returns, volatility = calculate_metrics(df)

  # Interactive Comeback Window
  print()
  print("--- K-Quant Comeback Window Analyzer ---")
  user_date = input("Enter a comeback date between Jan. 2023 - today (Format: YYYY-MM-DD): ")

  if not user_date.strip():
    print("No date entered. Please run the program again and enter a date like 2026-03-20.")
    raise SystemExit
  # handles the user just pressing Enter without typing anything

  # catches badly formatted dates (like "hello")
  try:
    user_date = user_date.strip().replace("/", "-")
    # removes extra spaces and swaps slashes for dashes so the chart filename works

    comeback_slice = get_event_window(returns, event_date=user_date, window_days=15)

    if len(comeback_slice) == 0:
       print(f"No data found for {user_date}.")
    else:
       print()    
       print(f"Results for {user_date} (Showing preview):")
       print(comeback_slice.head())
       print()
       print(f"Total trading days captured in this window: {len(comeback_slice)}")

       analyze_comeback_volatility(volatility, user_date, window_days=15)

       plot_event_window(comeback_slice, user_date)
       # I had the two function calls switched around but realized that 
       # analyze_comeback_volatility would never run unless the user closed the chart
       # so I decided to switch them around.
       
        
  except Exception as e:
    print(f"An error occurred: {e}")
    print("Check your date format. Make sure it's YYYY-MM-DD and is after 2023 (until today).")
