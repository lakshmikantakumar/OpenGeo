import sys
import os
import argparse
from osgeo import gdal, ogr
from file.exist import check_field_exists, check_file_exists

def rasterize_vector(input_vector, attribute_name, pixel_size, output_raster):
    """
    Rasterize a vector file using the information from the vector's extent and a user-provided pixel size.
    
    Parameters:
    - input_vector: Path to the input vector file (e.g., Shapefile, GeoJSON).
    - attribute_name: The name of the attribute field to be used as the burn-in value.
    - pixel_size: Pixel resolution (xres, yres) to use for the output raster.
    - output_raster: Path to the output raster file (e.g., GeoTIFF).
    """
    # Check if the input vector file exists
    if not check_file_exists(input_vector):
        return  # Stop execution if file is missing

    # Check if the attribute exists in the vector file
    if not check_field_exists(input_vector, attribute_name):
        print(f"Error: Attribute '{attribute_name}' not found in the vector file.")
        return

    # Set the pixel size (resolution)
    xres, yres = pixel_size, pixel_size

    # Create the raster from the vector file using gdal_rasterize
    options = [
        "-a", attribute_name,  # Attribute field name to use as burn value
        "-tr", str(xres), str(yres),  # Pixel resolution (xres, yres)
        "-of", "GTiff",  # Output format (GeoTIFF)
        "-co", "COMPRESS=LZW",  # Apply LZW compression
    ]
    
    # Rasterize the vector file using the gdal_rasterize tool
    try:
        gdal.Rasterize(output_raster, input_vector, options=options)
        print(f"Rasterization successful! Output saved to: {output_raster}")
    except Exception as e:
        print(f"Error during rasterization: {e}")

def main():
    # Set up argument parsing for command-line execution
    parser = argparse.ArgumentParser(description="Rasterize a vector file using its extent and a user-defined pixel size.")
    parser.add_argument("input_vector", help="Path to the input vector file (e.g., Shapefile, GeoJSON).")
    parser.add_argument("attribute_name", help="The name of the attribute field to use as the burn value.")
    parser.add_argument("pixel_size", type=float, help="Pixel size (resolution) for the output raster.")
    parser.add_argument("output_raster", help="Path to the output raster file (e.g., GeoTIFF).")
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Call the rasterization function
    rasterize_vector(args.input_vector, args.attribute_name, args.pixel_size, args.output_raster)

if __name__ == "__main__":
    main()
