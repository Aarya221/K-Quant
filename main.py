import pandas as pd
# Import the pandas library, which is used for organizing and analyzing data in tables (DataFrames)

import yfinance as yf
# Import the yfinance library, which connects to Yahoo Finance to download historical stock prices

import matplotlib.pyplot as plt

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

    plt.savefig(f"output/comeback_{event_date}.png")
    print(f"\nChart saved as: output/comeback_{event_date}.png")
    
    plt.show()




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

    print()    
    print(f"Results for {user_date} (Showing preview):")
    print(comeback_slice.head())
    print()
    print(f"Total trading days captured in this window: {len(comeback_slice)}")

    plot_event_window(comeback_slice, user_date)
        
  except Exception as e:
    print("Check your date format. Make sure it's YYYY-MM-DD and is after 2023 (until today).")
