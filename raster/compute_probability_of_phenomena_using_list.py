import os
import rasterio
import numpy as np
import argparse

def compute_probability_of_phenomena(tiff_list, pixel_value_of_phenomena, output_path):
    """
    Compute the probability of the phenomena based on a list of raster files, processing one raster at a time using block_windows.
    This approach handles large files efficiently by processing raster blocks.

    Parameters:
        tiff_list (list of str): List of paths to the input TIFF files.
        pixel_value_of_phenomena (int): The pixel value representing the phenomena to calculate probability for.
        output_path (str): Path to the output TIFF file where the computed probability will be saved.
    """
    # Initialize variables for CRS (Coordinate Reference System), bounds, and transform
    crs = None
    bounds = None
    transform = None

    # Read the first raster to initialize metadata and window sizes
    with rasterio.open(tiff_list[0]) as src:
        crs = src.crs
        bounds = src.bounds
        transform = src.transform

        # Initialize an array to store the total occurrence of the phenomena
        height, width = src.shape
        total_occurrences = np.zeros((height, width), dtype=np.int32)

    # Count the number of rasters to normalize the probability
    total_rasters = len(tiff_list)

    # Process each raster one by one
    for idx, tiff_path in enumerate(tiff_list):
        with rasterio.open(tiff_path) as src:
            # Process the raster in blocks using block_windows for memory efficiency
            for ji, window in src.block_windows():
                # Read data from the window
                data = src.read(1, window=window)

                # Update the total occurrences matrix: add 1 where the phenomena is present
                total_occurrences[window.row_off:window.row_off + window.height, window.col_off:window.col_off + window.width] += (data == pixel_value_of_phenomena)

        # Print progress of raster processing
        print(f"Processed {idx + 1}/{total_rasters} rasters...")

    # Compute the probability by dividing total occurrences by the number of rasters
    probability_of_phenomena = total_occurrences / total_rasters

    # Save the computed probability to a new TIFF file
    with rasterio.open(output_path, 'w', 
                        driver='GTiff', 
                        height=height, 
                        width=width, 
                        count=1, 
                        dtype=rasterio.float32, 
                        crs=crs, 
                        transform=transform,
                        compress='LZW') as dst:
        dst.write(probability_of_phenomena, 1)

    print(f"Probability of phenomena saved to {output_path}")

def parse_args():
    """
    Parse command-line arguments using argparse.
    
    Returns:
        args (Namespace): A Namespace object containing the command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Compute the probability of phenomena in raster files")
    
    # Add argument for input TIFF files (can be a list of paths)
    parser.add_argument('tiff_files', metavar='TIFF_FILES', type=str, nargs='+', 
                        help="List of input raster (TIFF) file paths.")
    
    # Add argument for the pixel value of the phenomena to track
    parser.add_argument('pixel_value', type=int, 
                        help="The pixel value representing the phenomena to track.")
    
    # Add argument for the output file path
    parser.add_argument('output_path', type=str, 
                        help="Path to the output TIFF file where the computed probability will be saved.")
    
    # Parse the arguments
    return parser.parse_args()

def main():
    # Parse command-line arguments
    args = parse_args()

    # Call the function to compute the probability of phenomena
    compute_probability_of_phenomena(args.tiff_files, args.pixel_value, args.output_path)

if __name__ == "__main__":
    main()
