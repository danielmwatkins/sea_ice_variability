import os
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Define the directory containing the buoy data and the output folder
buoy_data_dir = "/Users/aless/Desktop/sea_ice_variability/data/buoy_data/mosaic_dn2"
output_folder = os.path.join(buoy_data_dir, "truncated_plots")

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"Created folder: {output_folder}")

# List all CSV files in the directory
buoy_files = [f for f in os.listdir(buoy_data_dir) if f.endswith('.csv')]

# Function to process and plot buoy data
def process_buoy_data(file_path):
    print(f"Processing file: {file_path}")

    # Load the CSV file into a DataFrame
    try:
        df = pd.read_csv(file_path, parse_dates=['datetime'], index_col='datetime')
        print(df.head())  # Print first few rows to verify data structure
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return

    # Check if 'datetime', 'latitude', 'longitude' columns exist
    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        print(f"Skipping {file_path}: 'latitude' or 'longitude' column missing.")
        return

    # Truncate to the region with the most data (customize the truncation if necessary)
    df_truncated = df.resample('1h').mean()
    print(f"Data shape after resampling: {df_truncated.shape}")  # Check if there is data

    if df_truncated.empty:
        print(f"No data after resampling for {file_path}, skipping...")
        return

    # Create a polar stereographic map plot with Cartopy
    plt.figure(figsize=(12, 10))
    ax = plt.axes(projection=ccrs.NorthPolarStereo())

    # Add coastlines and gridlines for context
    ax.coastlines(resolution='110m')
    ax.gridlines(draw_labels=True)

    # Add land and ocean features for better context
    ax.add_feature(cfeature.LAND, zorder=0)
    ax.add_feature(cfeature.OCEAN, zorder=0)

    # Plot the buoy trajectory
    sc = plt.scatter(df_truncated['longitude'], df_truncated['latitude'], 
                     c=df_truncated.index, cmap='viridis', transform=ccrs.PlateCarree(), 
                     s=20, label='Buoy Trajectory')

    # Add a color bar to represent time progression
    cbar = plt.colorbar(sc, ax=ax, orientation='horizontal', pad=0.1)
    cbar.set_label('Datetime (Specific)', fontsize=12)

    # Customize the color bar labels to include date and time information
    cbar.ax.set_xticklabels([pd.to_datetime(tick).strftime('%Y-%m-%d %H:%M') for tick in cbar.get_ticks()])

    # Add labels and title
    plt.title(f'Buoy Trajectory (Lat/Lon) - {os.path.basename(file_path)}', fontsize=16)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.legend(loc='upper right')

    # Save the figure to the output folder
    image_file_name = f"{os.path.basename(file_path).replace('.csv', '_polar_plot.png')}"
    print(f"Saving plot for {file_path}")
    plt.savefig(os.path.join(output_folder, image_file_name))
    plt.close()  # Close the figure after saving

# Loop through all files in the directory and process them
for file_name in buoy_files:
    file_path = os.path.join(buoy_data_dir, file_name)
    process_buoy_data(file_path)

print(f"All truncated polar map plots have been saved in the folder: {output_folder}")
