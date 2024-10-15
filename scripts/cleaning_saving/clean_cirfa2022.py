import os
import pandas as pd
import numpy as np

from icedrift.cleaning import check_positions, check_gaps

# Define the path to the folder containing the raw CSV files
folder_path = "../../data/buoy_data/cirfa2022/"

# Create a new directory for the cleaned data
cleaned_data_folder = os.path.join(folder_path, 'cleaned_data')
if not os.path.exists(cleaned_data_folder):
    os.makedirs(cleaned_data_folder)

# List all CSV files in the folder
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# Define the cleaning function
def clean_buoy_data(df):
    # Convert 'datetime' column to a proper datetime object
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    
    # Convert latitude and longitude to numeric, drop invalid rows
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df_cleaned = df.dropna(subset=['longitude', 'latitude'])
    
    # Remove rows where latitude or longitude is outside the valid range
    df_cleaned = df_cleaned[(df_cleaned['latitude'].between(-90, 90)) & (df_cleaned['longitude'].between(-180, 180))]
    
    # Check for duplicated or nonphysical positions
    flag_positions = check_positions(df_cleaned, pairs_only=True)
    df_cleaned = df_cleaned[~flag_positions]
    
    # Check for gaps in data
    flag_gaps = check_gaps(df_cleaned, threshold_gap='4h', threshold_segment=12)
    df_cleaned = df_cleaned[~flag_gaps]
    
    return df_cleaned

# Iterate over the CSV files, clean them, and save the cleaned files
for file in csv_files:
    print(f'Processing file: {file}')
    
    # Load each CSV file into a DataFrame
    file_path = os.path.join(folder_path, file)
    df = pd.read_csv(file_path, header=None, names=['datetime', 'latitude', 'longitude'])
    
    # Clean the data
    df_cleaned = clean_buoy_data(df)
    
    # Save the cleaned data to a new CSV file in the 'cleaned_data' folder
    cleaned_file_path = os.path.join(cleaned_data_folder, file)
    df_cleaned.to_csv(cleaned_file_path, index=False)
    
    print(f'Cleaned file saved to: {cleaned_file_path}')

print("All files have been processed and cleaned!")
