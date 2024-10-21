import os
import pandas as pd
import numpy as np
import pyproj
import matplotlib.pyplot as plt

# Assuming icedrift is already installed and available in the path
from icedrift.analysis import compute_velocity
from icedrift.cleaning import check_positions, check_speed, check_gaps
from icedrift.interpolation import interpolate_buoy_track

# Define the directory containing the buoy data and the output folder
buoy_data_dir = '../../data/buoy_data/n-ice2015/cleaned_data'
output_folder = "../../data/buoy_data/n-ice2015/velocity_plots"

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"Created folder: {output_folder}")

# List all CSV files in the directory
buoy_files = [f for f in os.listdir(buoy_data_dir) if f.endswith('.csv')]

# Function to process each buoy dataset
def process_buoy_data(file_path):
    print(f"Processing file: {file_path}")

    # Load the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Convert 'datetime' column to a proper datetime object if available
    if 'datetime' not in df.columns:
        df['datetime'] = pd.to_datetime(df['Unnamed: 0'], errors='coerce')
    else:
        df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')

    # Remove any rows with NaT (missing datetime) values
    df_cleaned = df.dropna(subset=['datetime'])

    # Check for missing or invalid values (sanity check)
    print(df_cleaned.isnull().sum())  # Check for remaining missing data

    # Convert latitude and longitude to numeric, drop invalid rows using .loc[]
    df_cleaned.loc[:, 'longitude'] = pd.to_numeric(df_cleaned['longitude'], errors='coerce')
    df_cleaned.loc[:, 'latitude'] = pd.to_numeric(df_cleaned['latitude'], errors='coerce')
    df_cleaned = df_cleaned.dropna(subset=['longitude', 'latitude'])

    # Remove rows where latitude or longitude is outside the valid range
    df_cleaned = df_cleaned[(df_cleaned['latitude'].between(-90, 90)) & (df_cleaned['longitude'].between(-180, 180))]

    # Check for duplicated or nonphysical positions
    flag_positions = check_positions(df_cleaned, pairs_only=True)
    df_cleaned = df_cleaned[~flag_positions]

    # Check for gaps in data (assumes sequential data)
    flag_gaps = check_gaps(df_cleaned, threshold_gap='4h', threshold_segment=12)
    df_cleaned = df_cleaned[~flag_gaps]

    # Set 'datetime' as the index for interpolation
    df_cleaned.set_index('datetime', inplace=True)

    # Check if there are valid datetime values to interpolate
    if df_cleaned.index.min() is not pd.NaT and df_cleaned.index.max() is not pd.NaT:
        # Interpolate using a 1-hour interval
        df_resampled = interpolate_buoy_track(df_cleaned, freq='1H', maxgap_minutes=240)

        # Reset index after interpolation
        df_resampled.reset_index(inplace=True)

        # Rename 'datetime' to 'date' for compatibility with compute_velocity
        df_resampled.rename(columns={'datetime': 'date'}, inplace=True)

        # Compute velocity using the interpolated data
        df_velocity = compute_velocity(df_resampled, date_index=False)

        # Plot the drift speed as a time series
        plt.figure(figsize=(10, 6))
        plt.plot(df_velocity['date'], df_velocity['speed'], label='Drift Speed (m/s)', color='green')
        plt.axhline(y=1.5, color='r', linestyle='--', label='1.5 m/s Threshold')
        plt.xlabel('Time')
        plt.ylabel('Speed (m/s)')
        plt.title(f'Buoy Drift Speed Over Time - {os.path.basename(file_path)}')
        plt.legend()

        # Save the figure to the output folder
        image_file_name = f"{os.path.basename(file_path).replace('.csv', '_velocity_plot.png')}"
        plt.savefig(os.path.join(output_folder, image_file_name))
        plt.close()  # Close the figure after saving
    else:
        print(f"Skipping file: {file_path} - No valid datetime values for interpolation.")

# Loop through all files in the directory and process them
for file_name in buoy_files:
    file_path = os.path.join(buoy_data_dir, file_name)
    process_buoy_data(file_path)

print(f"All images have been saved in the folder: {output_folder}")
