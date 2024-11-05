import os
import geopandas as gpd
from shapely.geometry import Point

def process_intersections(bank_lines_folder, centerline_folder, output_folder):
    """
    Process the intersections between river bank lines and centerlines in two folders, saving the intersection points to an output folder.

    This function finds intersection points between corresponding bank line and centerline shapefiles based on their filenames,
    and saves the points where the centerline intersects the bank lines to a new shapefile.

    Parameters:
    ----------
    bank_lines_folder : str
        Path to the folder containing shapefiles with the river bank lines (should contain exactly two LineString geometries).

    centerline_folder : str
        Path to the folder containing shapefiles with the river centerlines (should contain exactly one LineString geometry).

    output_folder : str
        Path to the folder where the intersection points will be saved.

    How it works:
    ------------
    1. **List Files**: Lists the shapefiles from both `bank_lines_folder` and `centerline_folder`.
    2. **Match Files**: For each bank line shapefile, it attempts to find the corresponding centerline shapefile by modifying the filename.
    3. **Load Geometries**: Loads both the bank line and centerline geometries.
    4. **Find Intersections**: Identifies points where the centerline intersects the bank lines.
    5. **Save Results**: Saves the intersection points as a new shapefile in the output folder.


    Notes:
    ------
    - Bank line shapefiles should have two `LineString` geometries, and centerline shapefiles should have one.
    - Intersecting points are saved in the same CRS (coordinate reference system) as the input files.
    - The function handles errors such as missing corresponding shapefiles or incorrect geometry counts.
    """

    # Get a list of all shapefiles in both folders
    bank_line_files = [f for f in os.listdir(bank_lines_folder) if f.endswith('.shp')]
    centerline_files = [f for f in os.listdir(centerline_folder) if f.endswith('.shp')]

    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Loop through all bank line shapefiles
    for bank_file in bank_line_files:
        # Construct full paths for bank line and centerline files
        bank_line_path = os.path.join(bank_lines_folder, bank_file)

        # Try to find the corresponding centerline file (matching the name part before the extension)
        centerline_file = bank_file.replace('_lines.shp', '_korr.shp')
        centerline_path = os.path.join(centerline_folder, centerline_file)

        if not os.path.exists(centerline_path):
            print(f"No corresponding centerline file found for {bank_file}")
            continue

        # Load the bank lines and centerline shapefiles
        bank_lines_gdf = gpd.read_file(bank_line_path)
        centerline_gdf = gpd.read_file(centerline_path)

        # Check if the shapefiles have the correct number of geometries
        if len(bank_lines_gdf) != 2:
            print(f"The bank lines shapefile {bank_file} must contain exactly two LineString geometries.")
            continue

        if len(centerline_gdf) != 1:
            print(f"The centerline shapefile {centerline_file} must contain exactly one LineString geometry.")
            continue

        # Extract the geometries
        bank_line1 = bank_lines_gdf.geometry.iloc[0]  # First river bank line
        bank_line2 = bank_lines_gdf.geometry.iloc[1]  # Second river bank line
        centerline = centerline_gdf.geometry.iloc[0]  # River centerline

        # Find the intersection between the centerline and bank lines
        intersection_points = []

        if centerline.intersects(bank_line1):
            intersection1 = centerline.intersection(bank_line1)
            if not intersection1.is_empty:
                if isinstance(intersection1, Point):
                    intersection_points.append(intersection1)
                elif hasattr(intersection1, 'geoms'):
                    intersection_points.extend([geom for geom in intersection1.geoms if isinstance(geom, Point)])

        if centerline.intersects(bank_line2):
            intersection2 = centerline.intersection(bank_line2)
            if not intersection2.is_empty:
                if isinstance(intersection2, Point):
                    intersection_points.append(intersection2)
                elif hasattr(intersection2, 'geoms'):
                    intersection_points.extend([geom for geom in intersection2.geoms if isinstance(geom, Point)])

        # If we found intersection points, save them to a shapefile
        if intersection_points:
            # Create a GeoDataFrame for the intersection points
            intersection_gdf = gpd.GeoDataFrame(geometry=intersection_points, crs=centerline_gdf.crs)

            # Define the output file path (with the same name as the centerline file)
            output_file_path = os.path.join(output_folder, centerline_file)

            # Save the intersection points to the output folder
            intersection_gdf.to_file(output_file_path)
            print(f"Intersection points saved to {output_file_path}")
        else:
            print(f"No intersections found between {centerline_file} and {bank_file}.")

# Define paths and run the function on all shapefiles

bank_lines_folder = r'T:\Abteilung 7\Müller\TEMP_Timis_Gewässerachsen\VISDOM\Bank_line'
centerline_folder = r'T:\Abteilung 7\Müller\TEMP_Timis_Gewässerachsen\VISDOM\Gewaesserachse'
output_folder = r'T:\Abteilung 7\Müller\TEMP_Timis_Gewässerachsen\VISDOM\check_intersection_2'

process_intersections(bank_lines_folder, centerline_folder, output_folder)
