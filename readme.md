# Sharpe ratio and volatility calculation

This script takes a list of stocks as input and creates a portfolio where $10000 is equally distributed among all the stocks. 

The portfolio returns, the standard deviation, and sharpe ratio of the portfolio are calculated.

All the input and output files will be stored in the data folder.

## Prerequisites

1. Python 3.x
2. Alphavantage premium key

##Steps to run:

1. In the terminal, run 
```pip3 install -r requirements.txt```
   
2. Get a premium key from [Alphavantage](https://www.alphavantage.co/documentation/) (necessary to get Adjusted close prices) and set in configs.
3. Create input in the format shown in "input.csv". Specify the start and end date in configs.
4. Run ```python3 price_getter.py```. Prices will be saved in "price.csv".
5. Change the name of the first column in "price.csv" from "index" to "Date" and save.
6. Run ```python3 sharpe_ratio_calculator.py```
7. The metrics will be printed in the format shown below. The returns data for the portfolio will be saved in "output.xlsx"


Tip: To get benchmark performance, create input.csv with a single row containing the benchmark stock, e.g SPY.

### Feedback and requests

Write to us at marketsentiment.live@gmail.com. Check out our analyses at [Market Sentiment](https://marketsentiment.substack.com).