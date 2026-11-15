import pandas as pd
# Import the pandas library, which is used for organizing and analyzing data in tables (DataFrames)

import yfinance as yf
# Import the yfinance library, which connects to Yahoo Finance to download historical stock prices

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

    print()
    print("Data preview (First 5 rows):")
    print(data.head())
    # .head() prints just the first 5 rows of the data table to preview

    return data
    # Return the downloaded data table so it can be saved to a variable


if __name__ == "__main__":
  df = fetch_stock_data()
  # Call the function from above and store the result inside df