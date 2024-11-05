import geopandas as gpd
import os

def reproject_shapefiles(folder_path, target_epsg):
    """
    Reproject all shapefiles in a given folder to the target EPSG code.

    Parameters:
    folder_path (str): The path to the folder containing the shapefiles.
    target_epsg (int): The EPSG code to which the shapefiles should be reprojected.

    Returns:
    None
    """
    # List all shapefiles in the folder
    shapefiles = [f for f in os.listdir(folder_path) if f.endswith('.shp')]

    # Loop through each shapefile
    for shapefile in shapefiles:
        shapefile_path = os.path.join(folder_path, shapefile)

        try:
            # Load the shapefile using GeoPandas
            gdf = gpd.read_file(shapefile_path)

            # Check and print the current EPSG code
            if gdf.crs is not None:
                current_epsg = gdf.crs.to_epsg()
                print(f"Shapefile: {shapefile} | Current EPSG: {current_epsg}")

                # Reproject if necessary
                if current_epsg != target_epsg:
                    print(f"Reprojecting {shapefile} to EPSG:{target_epsg}...")
                    gdf = gdf.to_crs(epsg=target_epsg)

                    # Save the reprojected shapefile back to the folder
                    new_shapefile_path = os.path.join(folder_path, f"reprojected_{shapefile}")
                    gdf.to_file(new_shapefile_path)
                    print(f"Saved reprojected shapefile: {new_shapefile_path}")
                else:
                    print(f"{shapefile} is already in EPSG:{target_epsg}")
            else:
                print(f"Shapefile: {shapefile} | CRS: Not defined")

        except Exception as e:
            print(f"Error processing {shapefile}: {e}")

# Example usage:
folder_path=r'T:\Abteilung 7\Müller\TEMP_Timis_Gewässerachsen\VISDOM\Bank_line'
target_epsg=25832
reproject_shapefiles(folder_path,target_epsg)
