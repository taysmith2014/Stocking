from .tiingo_test import *
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import requests
import datetime
import json
import numpy as np
import math

# Get traces for the main performance graphic
def get_traces(historical_data_df, performance, initial_money, weights, color_map):
    # Calculating money over time with initial_money invested
    money = initial_money + (initial_money * (performance / 100))
    money = np.around(money, 2)

    dollar_money = ["$" + str(entry) for entry in money]

    performance_df = pd.DataFrame({'dates': historical_data_df.loc[:,'date'], 'percent change': performance, 'money': dollar_money})

    symbols = list(historical_data_df.columns)[1:]
    if len(symbols) == 1:
        name = symbols[0]
    else:
        name = "Overall Portfolio"
    
    performance_trace = go.Scatter(x=performance_df.loc[:,'dates'], 
                                                    y=performance_df.loc[:,'percent change'],
                                                    mode='lines',
                                                    name = name,
                                                    text = performance_df.loc[:,'money'],
                                                    hovertemplate = 
                                                    '<i>Percent change<i>: %{y:.2f}' + '%' +
                                                    '<br><i>Money<i>: %{text}',
                                                    marker_color = color_map[name])
    return (performance_trace)

# Get pie charts for initial investment and ending investment
def get_pies(historical_data_df, initial_money, weights, color_map):
    individual_stock_initial = []
    individual_stock_performance = []

    symbols = list(historical_data_df.columns)
    symbols = symbols[1:]

    for ticker in symbols:
        # Find out the specific money allocated to each stock to start
        allocated_money = initial_money * weights[ticker]
        individual_stock_initial.append(allocated_money)

        # Find the percent change for that specific stock over interval
        percent_change = percentage_change(historical_data_df.loc[len(historical_data_df) - 1,ticker], historical_data_df.loc[find_first_non_nan(historical_data_df,ticker),ticker])
        individual_stock_performance.append(allocated_money + (allocated_money * (percent_change / 100)))
    
    end_performance_pie_df = pd.DataFrame({'stock': symbols, 'money': individual_stock_performance})
    end_pie = px.pie(end_performance_pie_df, values='money', names = 'stock', color_discrete_map = color_map, color='stock')

    beginning_percentage_pie_df = pd.DataFrame({'stock': symbols, 'money': individual_stock_initial})
    beginning_pie = px.pie(beginning_percentage_pie_df, values='money', names = 'stock', color_discrete_map = color_map, color='stock')

    return (beginning_pie, end_pie)

# Get the adjusted Close price for list_of_tickers over interval
def get_historical_data(list_of_tickers, interval):
    historical_data_df = pd.DataFrame()

    # Loop through tickers passed
    for ticker in list_of_tickers:
        # Get the stock data over interval
        data = get_price_interval(ticker, interval)
        ticker_df = pd.DataFrame(data)
        
        # Only keep the columns we need
        adj_ticker_df = ticker_df[['date', 'adjClose']]

        # Rename adjClose to the specific ticker
        adj_ticker_df = adj_ticker_df.rename(columns={'adjClose': ticker})

        # If first ticker, use this as starting dataframe, else merge on date
        if historical_data_df.empty:
            historical_data_df = adj_ticker_df
        else:
            historical_data_df = historical_data_df.merge(adj_ticker_df, on='date', how='outer')
        
    return (historical_data_df)

# Calculate the performance of stocks given weights and historical_data_df
def calculate_performance(hist_data_df, weights, individual_stock):
    performance_array = []

    # Get list of tickers from the column names in dataframe
    list_of_tickers = list(hist_data_df.columns)
    list_of_tickers = list_of_tickers[1:]

    # Creating index map to easily keep track of the first date that stock is available.
    first_index_map = {}
    for ticker in list_of_tickers:
        first_index_map[ticker] = find_first_non_nan(hist_data_df,ticker)

    # Loop through each date
    for i in range(0, len(hist_data_df), 1):
        temp_performance = 0
        # For each date, calculate the % performance
        for ticker in list_of_tickers:
            # Calculate performance for this day, percent change for specific stock * percentage of portfolio
            # If this stock was nan on this day, skip this stock for the day
            if not math.isnan(hist_data_df.loc[i,ticker]):
                # Get the stock performance
                stock_performance = (percentage_change(hist_data_df.loc[i,ticker],hist_data_df.loc[first_index_map[ticker],ticker]))
                # Adjust for weight oh portfolio
                weighted_stock_performance = stock_performance * weights[ticker]

                # Two modes:
                # Individual stock - getting the performance of a singular stock, don't adjust by porfolio weight
                if individual_stock == True:
                    temp_performance = temp_performance + stock_performance
                # Whole set of stocks - adjust by weight in portfolio
                elif individual_stock == False:
                    temp_performance = temp_performance + weighted_stock_performance

        performance_array.append(temp_performance)

    return (np.array(performance_array))

# Helper function to get percentage change between 2 values
def percentage_change(new_value, original_value):
    return (((new_value - original_value) / original_value) * 100)

# Finds the first non nan value in a dataframe column, used to check if stock was not available
def find_first_non_nan(df, ticker):
    for i in range(0, len(df), 1):
        if not math.isnan(df.loc[i,ticker]):
            return (i)
    
    return (-1)