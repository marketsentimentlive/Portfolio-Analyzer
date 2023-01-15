import pandas as pd
import re
import requests
from configs import *

TICKER = "Stock"
TIME_SERIES_DAILY = "Time Series (Daily)"
ALPHAVANTAGE_URL = "https://www.alphavantage.co/query"
DATE = "Date"
TOTAL_POS = "Total Pos"
CUMULATIVE_RETURN = "Cumulative return"
DAILY_RETURN = 'Daily return'


def process_file(price_input, output_file):
    stock_prices = read_price_input(price_input)
    stock_performance = get_portfolio_performance(stock_prices)
    write_performance_output(stock_performance, output_file)
    calculate_sharpe_ratios(stock_performance)

def read_price_input(price_input):
    stock_prices = pd.read_csv(price_input)
    stock_prices = stock_prices[::-1]
    return stock_prices


def get_portfolio_performance(price_input: pd.DataFrame):
    date = "Date"
    normalized_performance_suffix = " Pos"
    banned_cols = [date, "VTRS"]
    ticker_columns = [column for column in price_input.columns if column not in banned_cols]
    INITIAL_VALUE = 10000
    allocation = 1/len(ticker_columns)
    normalized_columns = []
    for column in ticker_columns:
        normalized_column = column + normalized_performance_suffix
        price_input[normalized_column] = price_input[column]/price_input.iloc[0][column]
        price_input[normalized_column] = INITIAL_VALUE * allocation * price_input[normalized_column]
        normalized_columns.append(normalized_column)
    price_input[TOTAL_POS] = price_input[normalized_columns].sum(axis=1)
    price_input[DAILY_RETURN] = price_input[TOTAL_POS].pct_change(1)
    price_input[CUMULATIVE_RETURN] = price_input[TOTAL_POS]/price_input.iloc[0][TOTAL_POS]-1
    return price_input

def calculate_sharpe_ratios(stock_performance):
    def sharpe(df):
        return df[DAILY_RETURN].mean()/df[DAILY_RETURN].std()

    stock_sharpe = sharpe(stock_performance)
    annualize_factor = (252**0.5)
    stock_sharpe_annual = annualize_factor * stock_sharpe
    st_dev = stock_performance[DAILY_RETURN].std() * annualize_factor
    # print(f"Sharpe ratio of portfolio: {stock_sharpe}")
    print(f"Sharpe ratio of portfolio annualized: {stock_sharpe_annual}")
    print(f"Standard deviation of portfolio annualized: {st_dev}")


def write_performance_output(stock_performance, output_file):
    stock_performance.to_csv(output_file, index=False)


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


process_file(PRICE_INPUT, OUTPUT_FILE)