import os 
# lets Python interact with user's computer operating system

import pandas as pd
# Import the pandas library, which is used for organizing and analyzing data in tables (DataFrames)

import yfinance as yf
# Import the yfinance library, which connects to Yahoo Finance to download historical stock prices

import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings("ignore")
# Tells Python to hide noisy background warnings from external libraries like yfinance


tickers = {"HYBE": "352820.KS",
    "JYP": "035900.KQ",
    "YG": "122870.KQ",}
# Define a dictionary matching human-readable company names
# to their official Yahoo Finance exchange ticker codes

# Define a custom function to bundle all the data downloading 
def fetch_stock_data():
    print("Fetching stock data from Yahoo Finance")
    print()

    data = yf.download(list(tickers.values()), start = "2023-01-01", progress = False)
    # Download historical stock data using yfinance:
    # - list(tickers.values()) grabs just the ticker codes ("352820.KS", etc.) and puts it in a list (like a java array)
        # this is because yfinance expects a list of ticker codes 
    # - start = "2023-01-01" tells it to pull data starting from January 1, 2023
    # - progress = False hides the loading bar in the terminal

    data = data.dropna()
    # Handles missing values (drops rows where markets were closed or data is missing)
    # cleans data and stores it back into data variable 

    code_to_name = {}
    # Empty dictionary to hold swapped codes and names (because the printed data shows ticker codes
    # instead of company names)

    for name, code in tickers.items():
        code_to_name[code] = name
    # Makes the code the key, and the company name the value

    data = data.rename(columns=code_to_name)
    # Rename columns using Pandas .rename() method


    print()
    print("Data preview (First 5 rows):")
    print(data.head())
    # .head() prints just the first 5 rows of the data table to preview
    # but stores all data from the start date up to today

    return data
    # Return the downloaded data table so it can be saved to a variable


def calculate_metrics(data):
    print()
    print("Calculating daily percentage returns and rolling volatility")

    close_prices = data['Close']

    daily_returns = close_prices.pct_change() * 100
    # Calculate daily percentage returns (how much the price changed compared to the previous day as a %)

    
    rolling_volatility = close_prices.pct_change().rolling(window=20).std() * 100
    # Calculate rolling 20-day standard deviation (volatility)
    # .rolling(window=20) looks at a 20-day moving window, and .std() calculates the standard deviation
    
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
    """
    Extracts stock data in a 30-day window (+/- window_days) around a specific comeback date.
    """

    print()
    print(f"Extracting event window around comeback date: {event_date}")
    
    target_date = pd.to_datetime(event_date)
    # Converts the input date string into a Pandas datetime object so it can match table dates
    
    start_window = target_date - pd.Timedelta(days=window_days)
    end_window = target_date + pd.Timedelta(days=window_days)
    # Calculates the start and end dates for the window (-15 days and +15 days)
    # pandas timedelta helps you add and subtract dates (if not for this you would be 
    # subtracting 15 days from May 15 which does not make sense)


    window_data = df.loc[start_window:end_window]
    # .loc[] = slice the DataFrame and grab only the rows falling inside this date range
    # .loc lets you grab rows or columns by their actual names / labels

    return window_data



def plot_event_window(window_data, event_date):
    # plt.figure() = creates a new drawing canvas and sets its size to 10 inches wide by 5 inches tall
    plt.figure(figsize=(10, 5))

    # goes through every column (stock ticker) one by one so I can plot them together
    for column in window_data.columns:
        plt.plot(window_data.index, window_data[column], marker='o', label=column)
        # draws a line graph using dates on the x-axis and returns on the y-axis
        
    plt.axvline(pd.to_datetime(event_date), color='red', linestyle='--', label='Comeback Date')
    # draws a red dashed line right on the comeback date to mark the event
    
    plt.title(f"K-Pop Stock Reaction Around Comeback: {event_date}", fontsize=14)
    
    plt.xlabel("Date", fontsize=12)
    
    plt.ylabel("Daily Return (%)", fontsize=12)
    
    plt.axhline(0, color='gray', linestyle='-', linewidth=0.8)
    # draws a gray line at y=0 so I can easily see positive vs. negative returns

    plt.legend()
    # displays the legend box showing which line/color belongs to which company name
        
    
    plt.grid(True, linestyle=':', alpha=0.6)
    # dotted grid to make it easier to read values across the chart
    
    plt.xticks(rotation=45)
    
    plt.tight_layout()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    # os.path.abspath(__file__) finds the absolute path of this program
    # and os.path.dirname() strips the filename to give just the folder where main.py lives

    output_dir = os.path.join(script_dir, "output")
    # os.path.join() combines the program's folder path with the name "output" 
    # so Python knows the exact directory regardless of the operating system
    
    os.makedirs(output_dir, exist_ok=True)
    # os.makedirs() creates the output folder if it doesn't exist yet 
    #  and exist_ok=True ensures Python won't crash or throw an error if the folder is already there

    file_path = os.path.join(output_dir, f"comeback_{event_date}.png")
    # os.path.join() builds the final file path by combining the output folder 
    # with a unique filename containing the user's entered comeback date (example: comeback_2026-03-20.png)

    plt.savefig(file_path)

    print(f"Chart saved as: output/comeback_{event_date}.png")
    
    plt.show()


def analyze_comeback_volatility(volatility_df, event_date, window_days=15):
   print()
   print(f"--- Comeback Volatility Impact Analysis ({event_date}) ---")
   # Compares stock volatility during a comeback window vs. the overall baseline volatility.
    
   vol_slice = get_event_window(volatility_df, event_date, window_days)
   # Slice the volatility table around the event window using my existing function
    
   if len(vol_slice) == 0:
    print(f"No volatility data found for {event_date}.")
    return

    
   window_avg = vol_slice.mean()
   # Calculate average volatility during the comeback window
   # .mean() is a method from the pandas library 
    

   baseline_avg = volatility_df.mean()
   # Calculate average baseline volatility across all data from 2023 to today
    

   comparison_df = pd.DataFrame({"Comeback Window Volatility (%)": window_avg,
        "Baseline Average Volatility (%)": baseline_avg,
    })
   # Prints a comparison table for each agency
    

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
   # displays table with numbers rounded to 2 decimal places
   print()
   print("(If Volatility Spike is positive, the stock was wilder during the comeback than usual!)")

   print()
   print("--- Key Takeaways ---")
   print()
   for ticker, row in comparison_df.iterrows():
    spike = row["Volatility Spike (%)"]
    baseline = row["Baseline Average Volatility (%)"]
    window_val = row["Comeback Window Volatility (%)"]
        
    if spike > 0:
        print(f"{ticker}: Saw a {spike:.1f}% volatility spike.")
        print(f"  -> Translation: Instead of its usual calm daily price swings (~{baseline:.1f}%),")
        print(f"     its daily movements jumped to ~{window_val:.1f}% as the market reacted to the comeback hype.\n")
    else:
        print(f"{ticker}: Remained calm, dropping by {abs(spike):.1f}% compared to normal baseline behavior.\n")

    #Interpretation of results


if __name__ == "__main__":
  df = fetch_stock_data()
  # Call the function from above and store the result inside df

  returns, volatility = calculate_metrics(df)

  # Interactive Comeback Window
  print()
  print("--- K-Quant Comeback Window Analyzer ---")
  user_date = input("Enter a comeback date between Jan. 2023 - today (Format: YYYY-MM-DD): ")

  # Checks if the user entered a date outside the dataset range
  try:
    comeback_slice = get_event_window(returns, event_date=user_date, window_days=15)

    if len(comeback_slice) == 0:
       print(f"No data found {user_date}.")
    else:
       print()    
       print(f"Results for {user_date} (Showing preview):")
       print(comeback_slice.head())
       print()
       print(f"Total trading days captured in this window: {len(comeback_slice)}")

       analyze_comeback_volatility(volatility, user_date, window_days=15)

       plot_event_window(comeback_slice, user_date)
       
        
  except Exception as e:
    print(f"An error occurred: {e}")
    print("Check your date format. Make sure it's YYYY-MM-DD and is after 2023 (until today).")
