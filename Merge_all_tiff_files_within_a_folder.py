import os
import rasterio
from rasterio.merge import merge
import matplotlib.pyplot as plt
import numpy as np
import glob

def merge_tiffs(input_tiffs, output_tiff):
    """
    Merge multiple TIFF files into a single TIFF file.

    Parameters:
    - input_tiffs (list): List of paths to input TIFF files to be merged.
    - output_tiff (str): Path to save the merged TIFF file.

    Returns:
    - None
    """
    # List to store opened raster files
    src_files_to_mosaic = []

    # Open each TIFF file and add it to the list
    for tiff in input_tiffs:
        src = rasterio.open(tiff)
        src_files_to_mosaic.append(src)

    # Merge the opened raster files
    mosaic, out_trans = merge(src_files_to_mosaic)

    # Get metadata from one of the source raster files
    out_meta = src.meta.copy()

    # Update metadata with the new dimensions and transform
    out_meta.update({"driver": "GTiff",
                     "height": mosaic.shape[1],
                     "width": mosaic.shape[2],
                     "transform": out_trans})

    # Write the merged raster to disk
    with rasterio.open(output_tiff, "w", **out_meta) as dest:
        dest.write(mosaic)

# Example usage:
# Define the directory path containing TIFF files
directory_path = r'D:\Python\Tiff_files'                            ##### Only input from the user
# Get a list of all TIFF files in the specified directory
input_tiffs = glob.glob(os.path.join(directory_path, '*.tif'))

# Path to save the merged TIFF file
output_tiff = os.path.join(directory_path, 'merged_output.tif')


# Merge the TIFF files
merge_tiffs(input_tiffs, output_tiff)
print(f'Merged TIFF saved as {output_tiff}')
