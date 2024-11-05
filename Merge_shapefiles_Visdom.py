import geopandas as gpd  # Importing the geopandas library for handling geospatial data
import os  # Importing the os library to handle file paths and directories
import pandas as pd  # Importing pandas, used for data manipulation

# Folder containing the input shapefiles
input_folder = r'D:\Clemens\VISDOM\BGS\Export_Paket1\Export_Paket1\Gewaesserachse'

# Output file path where the combined shapefile will be saved
output_shapefile = r'D:\Clemens\VISDOM\BGS\Export_Paket1\Export_Paket1\Gewaesserachse_BGS_korr.shp'

# Get a list of all shapefiles in the folder by filtering for files that end with '.shp'
shapefiles = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.shp')]

# Initialize an empty list to hold the GeoDataFrames for each shapefile
gdfs = []

# Loop through each shapefile in the list
for shapefile in shapefiles:
    # Read the current shapefile into a GeoDataFrame
    gdf = gpd.read_file(shapefile)

    # Select only the columns 'GEWAESSER', 'GEWAESSERN', and 'geometry' from the GeoDataFrame
    gdf = gdf[['GEWAESSER', 'GEWAESSERN', 'geometry']]

    # Append the filtered GeoDataFrame to the list
    gdfs.append(gdf)

# Combine all the GeoDataFrames in the list into one single GeoDataFrame using pandas' concat function
# ignore_index=True ensures that the indices are reset in the combined GeoDataFrame
combined_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))

# Save the combined GeoDataFrame as a new shapefile at the specified output path
combined_gdf.to_file(output_shapefile)

# Print a confirmation message with the path to the saved shapefile
print(f"Combined shapefile saved at: {output_shapefile}")
