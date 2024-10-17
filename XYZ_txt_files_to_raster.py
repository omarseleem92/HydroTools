import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os
from geocube.api.core import make_geocube
import rasterio as rio
import numpy as np  # Import numpy for checking infinity

#Sample Data in text files
#32398770.97	5584764.32	60.430
#32398769.71	5584764.10	55.400

# Instructions:
# The user should define the following variables before running the script:
# - `epsg_code`: The EPSG code for the coordinate system being used (e.g., UTM Zone 32N uses EPSG:25832).
# - `resolution`: The resolution of the output raster grid in meters (e.g., (-1, 1) means a 1-meter resolution in both X and Y directions).

# Define the EPSG code for the coordinate system (e.g., UTM Zone 32N uses EPSG:25832)
epsg_code = 25832  # Set the EPSG code for the desired CRS
# Define the resolution for the raster output (in meters)
resolution = (-1, 1)  # X and Y resolution (1 meter in both directions)

# Step 1: Set the directory containing the input files and the output directory for saving raster files
# directory: The path to the folder containing the .asc files.
# output_dir: The path where the generated raster files will be saved.
directory = r'G:\Abteilung 7\71_2 Hochwasserschutz\Projekte\VISDOM\7-BasisModellFlussHW\Datenbereitstellung\Bund\Rhein\2409Landesamt557-640\Messung2020'
output_dir = r'D:\Clemens\VISDOM\Rhein\Raster_cube_utm'

# Step 2: Loop through each file in the directory and process files that have the .asc extension.
for filename in os.listdir(directory):
    if filename.endswith('.asc'):  # Check if the file has an .asc extension
        # Define input file path
        file_path = os.path.join(directory, filename)

        # Define the output raster file path
        output_raster = os.path.join(output_dir, f'{os.path.splitext(filename)[0]}_elevation_raster.tif')

        # Step 3: Check if the raster file already exists to avoid reprocessing
        if os.path.exists(output_raster):
            print(f"Skipping {filename}, raster already exists.")
            continue  # Skip this file if the raster file is already present

        try:
            # Step 4: Read the .asc file into a DataFrame
            # The file is assumed to be tab-delimited with no headers, so we specify custom column names: Easting, Northing, and Elevation.
            df = pd.read_csv(file_path, sep='\t', header=None, names=['Easting', 'Northing', 'Elevation'])

            # Explanation: Remove the leading '32' from the Easting values because the data is in UTM Zone 32.
            # The Easting values has a prefix 32 which represents the UTM Zone 32 data 
            # We remove this prefix to get the correct coordinates.
            # This is standard for data from Gewässer Bund in Germany.
            df['Easting'] = df['Easting'].astype(str).str.slice(2).astype(float)

            # Ensure that the data types for Northing and Elevation are numeric
            df['Northing'] = pd.to_numeric(df['Northing'], errors='coerce')
            df['Elevation'] = pd.to_numeric(df['Elevation'], errors='coerce')

            # Remove rows with NaN (Not a Number), infinity, or invalid data points
            df = df[~df.isin([np.nan, np.inf, -np.inf]).any(axis=1)]

            # If the DataFrame is empty after cleaning, skip this file with a warning
            if df.empty:
                print(f"Warning: {filename} resulted in an empty DataFrame after cleaning.")
                continue

            # Step 5: Convert the DataFrame to a GeoDataFrame, using Easting and Northing as the point geometry
            geometry = [Point(xy) for xy in zip(df['Easting'], df['Northing'])]
            gdf = gpd.GeoDataFrame(df, geometry=geometry)

            # Step 6: Set the CRS to the user-specified EPSG code
            # The EPSG code defines the coordinate system to be used. For UTM Zone 32N, this is EPSG:25832.
            gdf.set_crs(epsg=epsg_code, inplace=True)

            # Step 7: Convert the point data to a raster using the `make_geocube` function
            # The 'resolution' parameter is set by the user to define the output grid resolution in meters (e.g., -1 and 1 meters for X and Y).
            out_grid = make_geocube(vector_data=gdf, measurements=["Elevation"], resolution=resolution)

            # Step 8: Save the raster file to the specified output path
            out_grid["Elevation"].rio.to_raster(output_raster)

            # Confirm that the raster file has been successfully saved
            print(f"Raster saved successfully for {filename} at {output_raster}")

        except Exception as e:
            # Catch any errors during processing and print an error message
            print(f"Error processing {filename}: {e}")
