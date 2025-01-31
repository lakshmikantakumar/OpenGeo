import os
import rasterio
import numpy as np
import argparse

def check_rasters(rasters, crs, bounds, transform):
    """
    Check if all rasters have the same CRS, bounds (extent), and resolution (transform).
    """
    for tiff, src in rasters.items():
        if src.crs != crs:
            print(f"CRS mismatch: {tiff} has CRS {src.crs}, expected {crs}")
            return False
        if src.bounds != bounds:
            print(f"Extent mismatch: {tiff} has bounds {src.bounds}, expected {bounds}")
            return False
        if src.transform != transform:
            print(f"Resolution mismatch: {tiff} has resolution {src.transform}, expected {transform}")
            return False
    return True

def compute_probability_of_phenomena(tiff_folder, pixel_value_of_phenomena, output_path):
    """
    Compute the probability of the phenomena based on a series of raster files, processing one raster at a time using block_windows.
    This approach handles large files efficiently by processing raster blocks.
    """
    # Get all TIFF file names in the folder
    tiff_files = [f for f in os.listdir(tiff_folder) if f.endswith('.tif')]

    # Initialize variables for CRS, bounds, and transform
    crs = None
    bounds = None
    transform = None

    # Read the first raster to initialize metadata and window sizes
    with rasterio.open(os.path.join(tiff_folder, tiff_files[0])) as src:
        crs = src.crs
        bounds = src.bounds
        transform = src.transform

        # Initialize an array to store the total occurrence of the phenomena
        height, width = src.shape
        total_occurrences = np.zeros((height, width), dtype=np.int32)

    # Count the number of rasters to normalize the probability
    total_rasters = len(tiff_files)

    # Process each raster one by one
    for idx, tiff in enumerate(tiff_files):
        tiff_path = os.path.join(tiff_folder, tiff)
        with rasterio.open(tiff_path) as src:
            # Process the raster in blocks using block_windows
            for ji, window in src.block_windows():
                # Read data from the window
                data = src.read(1, window=window)

                # Update the total occurrences matrix: add 1 where the phenomena is present
                total_occurrences[window.row_off:window.row_off + window.height, window.col_off:window.col_off + window.width] += (data == pixel_value_of_phenomena)

        # Print progress
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
                        compress= 'LZW') as dst:
        dst.write(probability_of_phenomena, 1)

    print(f"Probability of phenomena saved to {output_path}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Compute the probability of phenomena based on a series of rasters.")
    parser.add_argument('tiff_folder', type=str, help="Path to the folder containing the input TIFF files")
    parser.add_argument('pixel_value_of_phenomena', type=int, help="Pixel value indicating the presence of the phenomenon (e.g., 1 for presence, 0 for absence)")
    parser.add_argument('output_path', type=str, help="Path where the output probability raster will be saved")

    args = parser.parse_args()

    # Call the function to compute probability of phenomena
    compute_probability_of_phenomena(args.tiff_folder, args.pixel_value_of_phenomena, args.output_path)

if __name__ == "__main__":
    main()
