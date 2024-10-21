import os
import pandas as pd
import matplotlib.pyplot as plt
from icedrift.analysis import compute_velocity

# Define the directory containing the buoy data and the output folder
buoy_data_dir = '../../data/buoy_data/cirfa2022/cleaned_data'
output_folder = "../../data/buoy_data/cirfa2022/velocity_plots"

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# List all CSV files in the directory
buoy_files = [f for f in os.listdir(buoy_data_dir) if f.endswith('.csv')]

# Function to process each buoy dataset and create velocity plots
def process_buoy_data(file_path):
    print(f"Processing file: {file_path}")

    # Load the CSV file into a DataFrame
    df = pd.read_csv(file_path, header=None, names=['datetime', 'latitude', 'longitude'])

    # Convert 'datetime' column to a proper datetime object
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')

    # Remove any rows with NaT (missing datetime) values
    df = df.dropna(subset=['datetime'])

    # Set 'datetime' as the index
    df.set_index('datetime', inplace=True)

    # Rename 'datetime' to 'date' for compatibility with compute_velocity
    df.reset_index(inplace=True)
    df.rename(columns={'datetime': 'date'}, inplace=True)

    # Compute velocity using the data
    df_velocity = compute_velocity(df, date_index=False)

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

# Loop through all files in the directory and process them
for file_name in buoy_files:
    file_path = os.path.join(buoy_data_dir, file_name)
    process_buoy_data(file_path)

print(f"All velocity plots have been saved in the folder: {output_folder}")
