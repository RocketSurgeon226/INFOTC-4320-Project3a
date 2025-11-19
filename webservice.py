import requests
import matplotlib.pyplot as plt
from datetime import datetime
import uuid
import os

def get_api_data(symbol, function):
    api_key = "2O7W9WY18QMH3DXR"
    if function == "TIME_SERIES_INTRADAY":
        interval = "5min"
        url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&interval={interval}&apikey={api_key}"
    else:
        url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={api_key}"
    
    response = requests.get(url)
    data = response.json()
    
    # Check if the response is valid
    if "Error Message" in data:
        raise ValueError(f"API Error: {data['Error Message']}")
    if "Note" in data:
        raise ValueError(f"API Notice: {data['Note']}")
    
    return data

def extract_time_series(data):
    for key in data.keys():
        if "Time Series" in key:
            return data[key]
    return None

def filter_data(time_series, start_date, end_date):
    filtered = {}
    for date_str, values in time_series.items():
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        if start_date <= date <= end_date:
            filtered[date] = float(values["4. close"])
    return dict(sorted(filtered.items()))

def plot_data(data, symbol, chart_type="line"):
    if not data:
        raise ValueError("No data to plot.")
    
    dates = list(data.keys())
    prices = list(data.values())

    plt.figure(figsize=(10,5))
    if chart_type == "bar":
        plt.bar(dates, prices)
    else:
        plt.plot(dates, prices, marker='o')

    plt.title(f"{symbol} Stock Prices")
    plt.xlabel("Date")
    plt.ylabel("Closing Price (USD)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    filename = f"stock_data_chart_{uuid.uuid4().hex}.png"
    filepath = os.path.join("static", filepath)
    plt.savefig(filepath)
    plt.close()
    return filename
