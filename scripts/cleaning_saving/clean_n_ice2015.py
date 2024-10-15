import os
import pandas as pd

# Define the path to the folder containing the N-ICE2015 CSV files
folder_path = "../../data/buoy_data/n-ice2015/"
output_folder = os.path.join(folder_path, "cleaned_data")

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# List all CSV files in the folder
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

def clean_nice2015_data(file_path):
    # Load each CSV file into a DataFrame
    df = pd.read_csv(file_path)
    
    # Rename the 'Unnamed: 0' column to 'datetime' if it exists
    if 'Unnamed: 0' in df.columns:
        df.rename(columns={'Unnamed: 0': 'datetime'}, inplace=True)
    
    # Convert 'datetime' column to datetime type
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')

    # Clean the data by removing invalid rows and converting to numeric
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df_cleaned = df.dropna(subset=['longitude', 'latitude'])

    # Remove rows where latitude or longitude is outside the valid range
    df_cleaned = df_cleaned[(df_cleaned['latitude'].between(-90, 90)) & (df_cleaned['longitude'].between(-180, 180))]

    return df_cleaned

# Iterate over the CSV files, clean each one, and save the cleaned file
for file in csv_files:
    file_path = os.path.join(folder_path, file)
    
    try:
        # Clean the data
        df_cleaned = clean_nice2015_data(file_path)
        
        # Save the cleaned data
        output_file_path = os.path.join(output_folder, f"cleaned_{file}")
        df_cleaned.to_csv(output_file_path, index=False)
        
        print(f"Processed and saved: {output_file_path}")
    
    except Exception as e:
        print(f"Error processing {file}: {e}")
