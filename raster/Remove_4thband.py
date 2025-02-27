"""
This script removes the 4 th and above bands, to keep only 3 bands
Author: Dr. Lakshmi Kantakumar Neelamsetti, GDD GDC, Survey of India
Date: 27-Jun-2024
Version:1.0

Remark: use only 8 bit images, the output form 8bit conversion script.
"""
import os
import rasterio
from rasterio.enums import Resampling
import argparse

def remove_4th_band(input_folder):
    """
    This function processes all the .tif files in the specified folder by removing the 4th band 
    and saving the modified files with a new name.

    Args:
    input_folder (str): Path to the folder containing .tif files to be processed.
    """
    for filename in os.listdir(input_folder):
        if filename.endswith('.tif'):
            filepath = os.path.join(input_folder, filename)

            with rasterio.open(filepath) as src:
                # Read the dataset's profile
                profile = src.profile

                # Check the number of bands in the raster file
                if src.count < 4:
                    print(f"Skipping {filename}: less than 4 bands.")
                    continue

                # Read all bands except the 4th band
                bands = [src.read(i) for i in range(1, src.count + 1) if i != 4]

                # Update the profile to reflect the new band count
                profile.update(count=src.count - 1)

                # Prepare the output filepath
                output_filepath = os.path.join(input_folder, filename.replace('.tif', '_modified.tif'))

                # Write the new raster file with the modified band count
                with rasterio.open(output_filepath, 'w', **profile) as dst:
                    for idx, band in enumerate(bands, start=1):
                        dst.write(band, idx)

                print(f"Processed and saved: {output_filepath}")

def main():
    """
    Main function to parse command-line arguments and call the function to remove the 4th band.
    """
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Remove the 4th band from raster (.tif) files in a directory.")

    # Command-line argument for input folder
    parser.add_argument("input_folder", help="The path to the folder containing .tif files.")

    # Parse command-line arguments
    args = parser.parse_args()

    # Call the function with the provided input folder path
    remove_4th_band(args.input_folder)

if __name__ == "__main__":
    # Execute the main function to start the script
    main()
