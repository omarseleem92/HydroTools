import geopandas as gpd
import numpy as np
import os
from shapely.geometry import LineString, MultiLineString
from shapely.ops import nearest_points

def find_nearby_segments(line1, line2, threshold):
    """
    Find segments of LineStrings where the distance between them is less than the threshold.

    This function compares two `LineString` or `MultiLineString` geometries and identifies
    the portions of the lines that are closer together than the specified threshold distance.
    It interpolates points along `line1`, finds the nearest corresponding points on `line2`,
    and extracts the segments where the two lines are within proximity.

    Parameters:
    ----------
    line1 : LineString or MultiLineString
        The first line geometry to be compared. It can be either a `LineString` or a `MultiLineString`.

    line2 : LineString or MultiLineString
        The second line geometry to be compared. It can be either a `LineString` or a `MultiLineString`.

    threshold : float
        The distance threshold (in spatial units, such as meters) that defines proximity.
        Segments where the distance between the two lines is less than this value will be extracted.

    Returns:
    -------
    segments : list of LineString
        A list of `LineString` geometries representing the segments where the distance between
        `line1` and `line2` is less than the specified threshold.
        If no such segments exist, the list will be empty.

    How it works:
    ------------
    1. Handles both `LineString` and `MultiLineString` geometries by splitting MultiLineStrings
       into individual `LineString` components.
    2. Interpolates points along `line1` at regular intervals (determined by the resolution)
       and finds the nearest points on `line2`.
    3. For each pair of nearest points, calculates the distance. If the distance is below the
       threshold, buffers are created around the points to define proximity segments.
    4. The intersection of these buffers with the original lines is used to identify
       potential nearby segments.
    5. Segments are appended to the result list, which is returned at the end.
    """
    segments = []

    # Handle both LineString and MultiLineString geometries
    line1_parts = list(line1.geoms) if isinstance(line1, MultiLineString) else [line1]
    line2_parts = list(line2.geoms) if isinstance(line2, MultiLineString) else [line2]

    for line1_part in line1_parts:
        for line2_part in line2_parts:
            for i in np.linspace(0, 1, 100000):  # Adjust num for finer resolution
                point1 = line1_part.interpolate(i, normalized=True)
                nearest_point2 = nearest_points(point1, line2_part)[1]
                distance = point1.distance(nearest_point2)

                if distance < threshold:
                    # Create a buffer around the points to identify segments
                    buffer_distance = threshold
                    buffer1 = point1.buffer(buffer_distance)
                    buffer2 = nearest_point2.buffer(buffer_distance)

                    # Use intersection to find the closest line segments
                    potential_segments1 = buffer1.intersection(line1_part)
                    potential_segments2 = buffer2.intersection(line2_part)

                    # Append the segments based on their types
                    if isinstance(potential_segments1, LineString):
                        segments.append(potential_segments1)
                    elif isinstance(potential_segments1, MultiLineString):
                        segments.extend(potential_segments1)

                    if isinstance(potential_segments2, LineString):
                        segments.append(potential_segments2)
                    elif isinstance(potential_segments2, MultiLineString):
                        segments.extend(potential_segments2)

    return segments

def process_shapefile(input_shapefile_path, output_shapefile_path, threshold):
    """
    Process the input shapefile and save the line segments where the distance between LineStrings is less than the threshold.

    This function loads a shapefile containing two `LineString` geometries, calculates the minimum distance between them,
    and extracts the segments of the lines where they are closer together than a specified distance threshold.
    The resulting segments are saved into a new shapefile at the given output path.

    Parameters:
    ----------
    input_shapefile_path : str
        The file path to the input shapefile that contains exactly two `LineString` geometries.

    output_shapefile_path : str
        The file path where the resulting shapefile with the nearby segments will be saved.

    threshold : float
        The distance threshold (in spatial units, such as meters). Line segments where the distance between the two
        `LineString` geometries is less than this threshold will be extracted and saved.

    Raises:
    -------
    ValueError:
        If the input shapefile does not contain exactly two `LineString` geometries, the function raises an error.

    How it works:
    ------------
    1. **Load Shapefile**: The function reads the shapefile at `input_shapefile_path` using `geopandas` and expects exactly
       two `LineString` geometries. If this condition is not met, a `ValueError` is raised.
    2. **Extract LineStrings**: The two `LineString` geometries are extracted from the shapefile for further processing.
    3. **Calculate Distance**: The minimum distance between the two lines is calculated. If the distance is greater than
       or equal to 2 meters, the function prints this information and does not perform further processing.
    4. **Find Nearby Segments**: If the lines are closer than the threshold, the `find_nearby_segments()` function is called
       to identify the portions of the lines that are within the specified distance.
    5. **Save Segments**: The resulting nearby segments are stored in a new `GeoDataFrame` and saved to the output file path
       as a shapefile.

    Notes:
    ------
    - The input shapefile must contain exactly two `LineString` geometries. The function assumes this as a requirement
      and raises an error if violated.
    - The result shapefile will use the same coordinate reference system (CRS) as the input shapefile.
    """
    # Load the shapefile
    gdf = gpd.read_file(input_shapefile_path)

    if len(gdf) != 2:
        raise ValueError("The shapefile must contain exactly two LineString geometries.")

    # Extract the LineStrings
    line1 = gdf.geometry.iloc[0]
    line2 = gdf.geometry.iloc[1]

    # Check the minimum distance between the two LineStrings
    distance = line1.distance(line2)
    print(input_shapefile_path)
    if distance >= 2:
        print(f"The minimum distance between the two LineStrings is {distance}, which is greater than or equal to 2 m.")
    else:
        print(f"The minimum distance between the two LineStrings is {distance} m.")

        # Find line segments where the distance between the lines is less than the threshold
        near_segments = find_nearby_segments(line1, line2, threshold)

        # Create a GeoDataFrame for the segments
        segments_gdf = gpd.GeoDataFrame(geometry=near_segments, crs=gdf.crs)

        # Save the segments to a new shapefile
        segments_gdf.to_file(output_shapefile_path)
        print(f"Line segments saved to {output_shapefile_path}")

def process_all_shapefiles_in_folder(bank_line_path, output_folder, threshold):
    """
    Process all shapefiles in the given folder, checking the distance between LineStrings
    and saving the result in the output folder.

    This function loops through all shapefiles in the specified input directory (`bank_line_path`),
    processes each one by identifying the segments of `LineString` geometries that are closer
    than the specified threshold distance, and saves the results in an output folder.

    Parameters:
    ----------
    bank_line_path : str
        The path to the folder containing input shapefiles. Each shapefile should contain exactly two `LineString` geometries.

    output_folder : str
        The path to the folder where the output shapefiles containing the nearby segments will be saved.

    threshold : float
        The distance threshold (in spatial units such as meters) to be used for identifying nearby segments.
        Segments where the distance between the two `LineString` geometries is less than this threshold will be saved.

    How it works:
    ------------
    1. **Ensure Output Directory Exists**: The function checks if the specified output folder exists, and if not,
       it creates the folder to store the resulting shapefiles.
    2. **Loop through Shapefiles**: It iterates over each `.shp` file in the specified `bank_line_path` folder.
    3. **Process Each Shapefile**: For each shapefile, the function constructs the input and output file paths and
       calls the `process_shapefile()` function to process it. The output is saved with a modified filename
       (appending "_segments" to the original filename).
    4. **Error Handling**: If there is an error while processing a particular shapefile (e.g., it does not contain
       valid geometries), the function catches the exception and prints an error message, but continues processing
       other files.

    Notes:
    ------
    - The input folder should contain shapefiles with exactly two `LineString` geometries.
      Each shapefile is processed separately.
    - Any errors encountered during the processing of individual shapefiles will be printed,
      but they will not stop the processing of other files.
    - The resulting shapefiles will be saved in the same CRS (coordinate reference system) as the input shapefiles.
    """
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Loop over all shapefiles in the directory
    for filename in os.listdir(bank_line_path):
        if filename.endswith(".shp"):
            input_shapefile_path = os.path.join(bank_line_path, filename)
            output_shapefile_path = os.path.join(output_folder, f"{filename[:-4]}_segments.shp")

            try:
                # Process each shapefile
                process_shapefile(input_shapefile_path, output_shapefile_path, threshold)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

# Define paths and run the function on all shapefiles
bank_line_path = r'T:\Abteilung 7\Müller\TEMP_Timis_Gewässerachsen\VISDOM\Bank_line'
output_folder = r'T:\Abteilung 7\Müller\TEMP_Timis_Gewässerachsen\VISDOM\check_distance_2'
threshold_distance = 2.0  # Set the distance threshold

process_all_shapefiles_in_folder(bank_line_path, output_folder, threshold_distance)
