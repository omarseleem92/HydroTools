import os
import geopandas as gpd
from shapely.geometry import LineString, MultiLineString
import numpy as n

'''
This script processes shapefiles of river centerlines and banklines to ensure that the banklines have the same drawing direction as the river centerline.
It also converts any geometries that are not LineString into LineString (did not work as expected).

'''

def get_direction_vector(line):
    """
    Calculate the direction vector of a LineString.

    Parameters:
    line : LineString
        The LineString whose direction vector is to be calculated.

    Returns:
    tuple
        A normalized direction vector (dx, dy).
    """
    start_point = np.array(line.coords[0])  # Get the starting point of the line
    end_point = np.array(line.coords[-1])    # Get the ending point of the line
    direction_vector = end_point - start_point  # Calculate the direction vector
    norm = np.linalg.norm(direction_vector)  # Calculate the norm (length) of the vector

    if norm == 0:
        return (0, 0)  # Return zero vector if the line length is zero

    return direction_vector / norm  # Return the normalized direction vector

def is_same_direction(line1, line2):
    """
    Check if two LineStrings have the same drawing direction based on their direction vectors.

    Parameters:
    line1 : LineString
        The first LineString (e.g., river centerline).
    line2 : LineString
        The second LineString (e.g., bankline).

    Returns:
    bool
        True if the direction of line1 and line2 is the same, False otherwise.
    """
    dir1 = get_direction_vector(line1)  # Get direction vector of the first line
    dir2 = get_direction_vector(line2)  # Get direction vector of the second line

    dot_product = np.dot(dir1, dir2)  # Calculate the dot product of the two direction vectors

    return dot_product > 0  # Return True if the vectors are in the same direction

def align_direction(line1, line2):
    """
    Align the direction of line2 with line1 if necessary.

    Parameters:
    line1 : LineString
        The reference LineString (e.g., river centerline).
    line2 : LineString
        The LineString to be aligned (e.g., bankline).

    Returns:
    LineString
        The aligned bankline with the same drawing direction as line1.
    """
    if is_same_direction(line1, line2):
        print('No need to change direction')  # Direction is already the same
        return line2  # Return the original bankline
    else:
        print('Reversing the bankline direction')  # Direction is different
        return LineString(line2.coords[::-1])  # Reverse the bankline direction

def convert_to_linestring(geometry):
    """
    Convert a geometry to a LineString if it's a MultiLineString or any other type.

    Parameters:
    geometry : geometry
        The geometry to be converted.

    Returns:
    LineString
        A LineString representation of the input geometry.

    Raises:
    ValueError
        If the geometry type is unsupported.
    """
    if isinstance(geometry, LineString):
        return geometry  # Return the LineString as is
    elif isinstance(geometry, MultiLineString):
        # Merge all LineStrings into a single LineString
        merged_coords = []
        for line in geometry.geoms:  # Iterate over individual LineStrings
            merged_coords.extend(line.coords)  # Collect coordinates
        return LineString(merged_coords)  # Return the merged LineString
    else:
        raise ValueError(f"Unsupported geometry type: {type(geometry)}")  # Raise error for unsupported types

def process_lines(line1, line2):
    """
    Process and align two geometries (either LineString or MultiLineString).

    Parameters:
    line1 : geometry
        The first geometry to be processed (e.g., river centerline).
    line2 : geometry
        The second geometry to be processed (e.g., bankline).

    Returns:
    LineString
        The aligned version of line2.
    """
    line1 = convert_to_linestring(line1)  # Convert the first line to LineString if needed
    line2 = convert_to_linestring(line2)  # Convert the second line to LineString if needed

    return align_direction(line1, line2)  # Align and return the second line

def process_shapefiles(river_centerline_path, banklines_path, output_folder):
    """
    Process the river centerline and banklines, ensuring their drawing directions align.

    Parameters:
    river_centerline_path : str
        Path to the shapefile containing the river centerline.
    banklines_path : str
        Path to the shapefile containing the banklines.
    output_folder : str
        Directory where the aligned shapefiles will be saved.
    """
    original_filename = os.path.basename(banklines_path)  # Extract original file name

    print(f"Processing {original_filename}")

    # Load the river centerline and banklines into GeoDataFrames
    river_gdf = gpd.read_file(river_centerline_path)
    banklines_gdf = gpd.read_file(banklines_path)

    # Extract the LineString geometries
    river_line = river_gdf.geometry.iloc[0]  # Assuming only one river centerline
    bankline1 = banklines_gdf.geometry.iloc[0]  # First bankline
    bankline2 = banklines_gdf.geometry.iloc[1]  # Second bankline

    # Align the bankline directions with the river centerline
    aligned_bankline1 = process_lines(river_line, bankline1)
    aligned_bankline2 = process_lines(river_line, bankline2)

    # Update the geometries in the GeoDataFrame
    banklines_gdf.geometry.iloc[0] = aligned_bankline1
    banklines_gdf.geometry.iloc[1] = aligned_bankline2

    # Ensure output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Save the aligned banklines with the same filename in the output folder
    output_banklines_path = os.path.join(output_folder, original_filename)
    banklines_gdf.to_file(output_banklines_path)  # Save the updated GeoDataFrame

    print(f"Aligned banklines saved to {output_banklines_path}\n")

def batch_process_shapefiles(river_folder, bankline_folder, output_folder):
    """
    Process all corresponding shapefiles in the river and bankline folders.

    Parameters:
    river_folder : str
        Directory containing river centerline shapefiles.
    bankline_folder : str
        Directory containing bankline shapefiles.
    output_folder : str
        Directory where the aligned shapefiles will be saved.
    """
    for river_filename in os.listdir(river_folder):
        if river_filename.endswith(".shp"):  # Check for shapefiles
            river_basename = os.path.splitext(river_filename)[0]  # Get base filename
            print(river_basename)
            bankline_filename = river_basename.replace('_korr', '_lines')  # Construct bankline filename
            print(bankline_filename)
            river_centerline_path = os.path.join(river_folder, river_filename)  # Full path for river centerline
            banklines_path = os.path.join(bankline_folder, bankline_filename + '.shp')  # Full path for banklines
            print(banklines_path)

            # Check if corresponding bankline file exists
            if os.path.exists(banklines_path):
                process_shapefiles(river_centerline_path, banklines_path, output_folder)  # Process files
            else:
                print(f"Warning: No corresponding bankline file found for {river_filename}")  # Warn if not found

# Define folders
river_folder = r'D:\Clemens\VISDOM\Shp\Final\Projected\Gewaesserachse'  # Folder for river shapefiles
bankline_folder = r'D:\Clemens\VISDOM\Shp\Final\Projected\Bank_line'  # Folder for bankline shapefiles
output_folder = r'D:\Clemens\VISDOM\Shp\Final\Projected\Bank_line_aligned'  # Folder for output files

# Run the batch processing
batch_process_shapefiles(river_folder, bankline_folder, output_folder)  # Start processing
