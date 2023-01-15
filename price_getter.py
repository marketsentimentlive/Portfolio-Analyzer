import pandas as pd
import re
import requests
from configs import *

TICKER = "Stock"
TIME_SERIES_DAILY = "Time Series (Daily)"
ALPHAVANTAGE_URL = "https://www.alphavantage.co/query"
DATE = "Date"

def pull_prices(input_file, price_input, start_date, end_date):
    records = read_input(input_file)
    records_with_prices = get_stock_prices(records, start_date, end_date)
    write_output(records_with_prices, price_input)

def read_input(input_file):
    if ".csv" in input_file:
        return pd.read_csv(input_file).to_dict(orient="records")
    elif ".xls" in input_file:
        return pd.read_excel(input_file).to_dict(orient="records")

def get_stock_prices(records, start_date, end_date):
    records_with_prices = []
    errored_tickers = []
    count = 0
    for record in records:
        count += 1
        try:
            time_series = get_prices_for_ticker(record, start_date, end_date)
            records_with_prices.append(time_series)
        except Exception as e:
            errored_tickers.append(record[TICKER])
        if count % 10 == 0:
            print(f"{count} records processed, {len(errored_tickers)} errors")
    print(f"Total errors: {len(errored_tickers)}")
    print(f"Unique errored tickers: {list(set(errored_tickers))}")
    price_df = pd.DataFrame.from_records(records_with_prices)
    price_df = price_df.set_index(TICKER).transpose()
    price_df.reset_index(inplace=True)
    return price_df

def get_prices_for_ticker(record, start, end):
    ADJ_CLOSE = "5. adjusted close"
    ticker = record[TICKER]
    ticker = re.sub(r"[\xa0]", "", ticker)
    record[TICKER] = ticker
    time_series = get_alpha_vantage_records(ticker)
    for date in time_series.keys():
        if date >= start and date <= end:
            record[date] = float(time_series[date][ADJ_CLOSE])
    return record


def get_alpha_vantage_records(ticker):
    params = {
        "symbol": ticker,
        "apikey": APIKEY,
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "outputsize": "full"
    }
    response = requests.get(ALPHAVANTAGE_URL, params)
    data = response.json()
    return data[TIME_SERIES_DAILY]


def write_output(output_df, output_file):
    output_df.to_csv(output_file, index=False)


pull_prices(INPUT_FILE, PRICE_INPUT, START_DATE, END_DATE)