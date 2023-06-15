import pandas as pd
import numpy as np
from datetime import date

def add_end_dates(input_filename: str, output_filename: str):
   # Import Data
    data = pd.read_csv(input_filename,parse_dates=['Campaign Date'])

    # Manipulate Data
    campaigns = data[['Campaign ID','Campaign Date','Link']].copy() # Copy subset of data to new dataframe
    duplicates = campaigns[campaigns.duplicated(['Link'])] # Isolate duplicate links
    duplicate_rows = set(duplicates['Link'].to_numpy()) # Create set from duplicates
    duplcate_campaigns = campaigns.loc[data.Link.isin(duplicate_rows)].copy() # Isolate campaigns with a duplicate link
    duplcate_campaigns = duplcate_campaigns.sort_values(by=['Campaign Date'],ascending=True) # Sort by Campaign Date
    duplcate_campaigns['End Date'] = duplcate_campaigns['Campaign Date'].shift(-1) - pd.DateOffset(days=1) # Set end date to day before next campaign start date
    duplcate_campaigns = duplcate_campaigns[['Campaign ID', 'End Date']] # Remove Unnecessary Columns
    data = data.join(duplcate_campaigns,rsuffix='_1') # Join the end dates to the main data frame
    data = data[['Campaign ID','Campaign Date','Campaign Name', 'Campaign Short Description',  
                'Premium Name','Campaign Group','Link ID','Link Type', 'Link', 'End Date']] # Remove Extra Row
    data['End Date'].fillna(date.today(),inplace=True) # Replace null end dates with today's date
    data['End Date'] = pd.to_datetime(data['End Date']) # Fix date formatting

    # Export Data
    data.to_csv(output_filename, index=False)

def main():
    add_end_dates('../Raw/Google_Sheets/Web_Campaign_Data.csv',  '../Raw/Google_Sheets/Web_Campaign_Data_Cleaned.csv')

if __name__ == '__main__':
    main()