# -*- coding: utf-8 -*-
"""
Created on Sun Aug 11 14:08:22 2024

@author: fisch
"""


import cot_reports as cot
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import yfinance as yf
from datetime import timedelta

pd.set_option('display.max_rows', None)

# Define the ticker and the start year
ticker = "SI=F"
start_year = 2015
end_year = datetime.now().year

# Create a list of years from start_year to end_year
years = list(range(start_year, end_year + 1))

# Create empty cot_df for concatination
columns=["com_net", "noncom_net"]
cot_df = pd.DataFrame(columns=columns)

# Creating a dictionary with ticker keys corresponding to the COT instrument names
ticker_name_dict = {
    "GC=F":"GOLD - COMMODITY EXCHANGE INC.",
    "SI=F":"SILVER - COMMODITY EXCHANGE INC.",
    "PA=F":"PALLADIUM - NEW YORK MERCANTILE EXCHANGE",
    "PL=F":"PLATINUM - NEW YORK MERCANTILE EXCHANGE",
    "HG=F":"COPPER- #1 - COMMODITY EXCHANGE INC.",
    "CL=F":"CRUDE OIL, LIGHT SWEET-WTI - ICE FUTURES EUROPE",
    "NG=F":"NAT GAS NYME - NEW YORK MERCANTILE EXCHANGE",
    "ZC=F":"CORN - CHICAGO BOARD OF TRADE",
    "ZW=F":"WHEAT-SRW - CHICAGO BOARD OF TRADE"
    }

# Transform the date to strings and download the historical price data
start_date_str = datetime(start_year, 1, 1).strftime("%Y-%m-%d")
end_date_str = datetime.today().strftime("%Y-%m-%d")
yf_df = yf.download(ticker, start=start_date_str, end=end_date_str)

# Set the index as datetime object and only use the adjusted close
yf_df.index = pd.to_datetime(yf_df.index)
yf_df = yf_df["Adj Close"]    

# Loop through every year in the years list
for year in years:        
    # Download the COT data and save it as cot_df_init
    cot_df_init = cot.cot_year(year = year, cot_report_type = 'legacy_fut')
    name = ticker_name_dict[ticker]
    
    # Filtering the dataframe to get relevant columns
    filtered_cot_df = cot_df_init[["Market and Exchange Names", "As of Date in Form YYYY-MM-DD","Commercial Positions-Long (All)","Commercial Positions-Short (All)",  "Noncommercial Positions-Long (All)", 
                      "Noncommercial Positions-Short (All)", "Change in Noncommercial-Long (All)", "Change in Noncommercial-Short (All)",
                      "% of OI-Noncommercial-Long (All)","% of OI-Noncommercial-Short (All)" ]]
    
    # Select only the data for the selected ticker
    filtered_cot_df_futures = filtered_cot_df[filtered_cot_df["Market and Exchange Names"].isin([f"{name}"])]
    
    # Rename for easier coding
    filtered_cot_df_futures = filtered_cot_df_futures.rename(columns={"As of Date in Form YYYY-MM-DD": 'date'})
    filtered_cot_df_futures = filtered_cot_df_futures.rename(columns={"Commercial Positions-Long (All)": "com_long"})
    filtered_cot_df_futures = filtered_cot_df_futures.rename(columns={"Commercial Positions-Short (All)": 'com_short'})
    filtered_cot_df_futures = filtered_cot_df_futures.rename(columns={"Noncommercial Positions-Long (All)": 'noncom_long'})
    filtered_cot_df_futures = filtered_cot_df_futures.rename(columns={"Noncommercial Positions-Short (All)": 'noncom_short'})
    
    # Transform the date column into datetime and set it as index
    filtered_cot_df_futures["date"] = pd.to_datetime(filtered_cot_df_futures["date"])
    filtered_cot_df_futures = filtered_cot_df_futures.set_index("date")
    
    # Calculat the net positions
    filtered_cot_df_futures["com_net"] = filtered_cot_df_futures["com_long"] - filtered_cot_df_futures['com_short']
    filtered_cot_df_futures["noncom_net"] = filtered_cot_df_futures["noncom_long"] - filtered_cot_df_futures['com_short']
    
    # Creating Variables for different futures instruments
    instrument = filtered_cot_df_futures[filtered_cot_df_futures["Market and Exchange Names"]== f"{name}"]
    instrument.index = pd.to_datetime(instrument.index)
    instrument = instrument[["com_net", "noncom_net"]]
    
    # Transform the index to datetime
    instrument.index = pd.to_datetime(instrument.index)
    
    # Concat the instrument df with the cot_df vertically (axis=0)
    cot_df = pd.concat([cot_df, instrument], axis=0)
    
    
# Concat the cot_df with the yf_df horizontally to create df    
df = pd.concat([yf_df, cot_df], axis=1)

# Transform all values to numeric to avoid plotting errors
df = df.apply(pd.to_numeric, errors="coerce")

# Forward fill NaNs to avoid plotting errors
df = df.ffill()    

# Initialize the plot with the rows
fig, (ax1, ax2, ax3) = plt.subplots(3,1, sharex=True, figsize=(12,8))

# Plot the price data with title beeing the value of the ticker_name_dict corresponding to ticker as key
ax1.plot(df.index,df["Adj Close"], color="black")
ax1.set_title(ticker_name_dict[ticker])
ax1.grid(True)

# Plot the 'com_net' column
ax2.plot(df.index, df["com_net"], color='black', label='com_net')
# Fill the area where 'com_net' is above 0 with green
ax2.fill_between(df.index, df["com_net"], where=(df["com_net"] > 0), color='green', alpha=0.3, label='Above 0')
# Fill the area where 'com_net' is below 0 with red
ax2.fill_between(df.index, df["com_net"], where=(df["com_net"] < 0), color='red', alpha=0.3, label='Below 0')
# Add title and grid
ax2.set_title('Commercials')
ax2.grid(True)

# Plot the 'noncom_net' column
ax3.plot(df.index, df["noncom_net"], color='black', label='com_net')
# Fill the area where 'noncom_net' is above 0 with green
ax3.fill_between(df.index, df["noncom_net"], where=(df["noncom_net"] > 0), color='green', alpha=0.3, label='Above 0')
# Fill the area where 'noncom_net' is below 0 with red
ax3.fill_between(df.index, df["noncom_net"], where=(df["noncom_net"] < 0), color='red', alpha=0.3, label='Below 0')
# Add title and grid
ax3.set_title('Non-commercials')
ax3.grid(True)

# Rotate the xticks on ax3
ax3.tick_params(axis='x', rotation=90)

# Show the plot
plt.show()
