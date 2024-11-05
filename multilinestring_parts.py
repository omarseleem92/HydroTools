import geopandas as gpd
import os
from shapely.geometry import LineString, MultiLineString

# Function to save each LineString from a MultiLineString into a separate shapefile
def save_linestrings_from_multilinestring(geometry, attributes, output_folder, base_filename, crs):
    """
    Save each LineString within a MultiLineString to separate shapefiles, using the same CRS as the input.
    
    Parameters:
    geometry : shapely.geometry.MultiLineString
        The MultiLineString geometry containing LineStrings.
    attributes : dict
        The attributes associated with the MultiLineString feature.
    output_folder : str
        The folder where the output shapefiles will be saved.
    base_filename : str
        The base name for the shapefiles.
    crs : dict or str
        The CRS (Coordinate Reference System) to use for the output shapefiles.
        
    Returns:
    None
    """
    if isinstance(geometry, MultiLineString):
        # Iterate over each LineString in the MultiLineString
        for i, linestring in enumerate(geometry.geoms):
            # Create a new GeoDataFrame for this LineString with the same CRS as the input
            gdf = gpd.GeoDataFrame(geometry=[linestring], crs=crs)
            
            # Add attributes to the GeoDataFrame
            for key, value in attributes.items():
                gdf[key] = value
            
            # Construct the base output file name using the GEWAESSER attribute
            gewasser_value = attributes.get('GEWAESSER', f"feature_{i+1}")  # Use GEWAESSER or fallback to feature index if not found
            output_filename = os.path.join(output_folder, f"{gewasser_value}_line_{i+1}.shp")
            
            # If the file already exists, add '_bank' to the filename
            if os.path.exists(output_filename):
                output_filename = os.path.join(output_folder, f"{gewasser_value}_line_{i+1}_bank.shp")
            
            # Save the LineString as a separate shapefile
            gdf.to_file(output_filename)
            print(f"Saved LineString to: {output_filename}")
    else:
        print(f"Geometry is not a MultiLineString: {geometry}")

# Load the shapefile
input_shapefile = r'G:\Abteilung 7\71_2 Hochwasserschutz\Projekte\VISDOM\7-BasisModellFlussHW\Bank-Polygone\TIMIS_Korrektur_LfU\Final\Bank_Lines.shp'  # Update with your input shapefile path
output_folder = r'G:\Abteilung 7\71_2 Hochwasserschutz\Projekte\VISDOM\7-BasisModellFlussHW\Bank-Polygone\TIMIS_Korrektur_LfU\Final\temp\Linestring\Bank_lines_20241015'  # Update with the output folder path

# Make sure output folder exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Read the input shapefile into a GeoDataFrame
gdf = gpd.read_file(input_shapefile)

# Get the CRS of the input shapefile
input_crs = gdf.crs

# Iterate over each feature (geometry) in the GeoDataFrame
for index, row in gdf.iterrows():
    geometry = row['geometry']  # Get the geometry of the current feature
    
    # Check if the geometry is a MultiLineString
    if isinstance(geometry, MultiLineString):
        attributes = row.drop('geometry').to_dict()  # Get all attributes except the geometry
        gewasser_value = attributes.get('GEWAESSER', f"feature_{index}")  # Get the GEWAESSER value or fallback
        save_linestrings_from_multilinestring(geometry, attributes, output_folder, gewasser_value, input_crs)
    else:
        print(f"Feature {index} is not a MultiLineString, skipping.")
