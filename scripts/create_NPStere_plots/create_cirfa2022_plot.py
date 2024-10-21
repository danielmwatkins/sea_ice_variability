import os
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Define the relative directory where the CSV files are located
buoy_data_dir = '../../data/buoy_data/cirfa2022/cleaned_data'
# Create an output directory for the plots (correct relative path)
output_folder = '../../data/buoy_data/cirfa2022/np_stere_plots'

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"Created folder: {output_folder}")

    # List all CSV files in the directory
buoy_files = [f for f in os.listdir(buoy_data_dir) if f.endswith('.csv')]

# Function to create a map for a single CSV file
def create_np_stere_plot(csv_file, output_dir):
    # Load the CSV data
    data = pd.read_csv(csv_file)
    
    # Define the map projection
    crs = ccrs.NorthPolarStereo(central_longitude=-45, true_scale_latitude=70)
    
    # Create a figure object
    fig = plt.figure(figsize=(5, 10))
    
    # Add subplot with North Polar Stereographic projection
    ax = fig.add_subplot(1, 1, 1, projection=crs)
    
    # Define the extent for the map
    ax.set_extent([0.2e6, 1.3e6, -2.15e6, -0.5e6], crs=crs)
    
    # Add land features to the map
    ax.add_feature(cfeature.LAND, color='k')
    
    # Plot the latitude and longitude data
    ax.plot(data['longitude'], data['latitude'], transform=ccrs.PlateCarree(), color='red', marker='o')
    
    # Save the figure to the output directory
    output_filename = os.path.join(output_dir, os.path.basename(csv_file).replace('.csv', '_np_stere_plot.png'))
    plt.savefig(output_filename)
    plt.close(fig)


# Loop through all CSV files in the cleaned_data directory
for filename in os.listdir(buoy_data_dir):
    if filename.endswith('.csv'):
        csv_file_path = os.path.join(buoy_data_dir, filename)
        create_np_stere_plot(csv_file_path, output_folder)

print("Plots created and saved successfully.")
