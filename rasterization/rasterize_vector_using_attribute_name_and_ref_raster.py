import os
import argparse
from osgeo import gdal
import rasterio
from raster.get_raster_info import get_raster_info
from file.exist import check_field_exists, check_file_exists

def rasterize_vector_using_field_name_and_ref_raster(input_vector, field_name, reference_raster, output_raster):
    """
    Rasterize a vector file using the information from get_raster_info.py.
    
    Parameters:
    - input_vector: Path to the input vector file (Shapefile, GeoJSON, etc.)
    - reference_raster: Path to the reference raster file (e.g., GeoTIFF)
    - field_name: The name of the attribute field to be used as the burn-in value
    - output_raster: Path to the output raster file (e.g., GeoTIFF)
    """
    # Check if the input files exist
    if not check_file_exists(input_vector) or not check_file_exists(reference_raster):
        return  # Stop execution if either file is missing

    # Check if the field exists in the vector file
    if not check_field_exists(input_vector, field_name):
        print(f"Error: Attribute Field'{field_name}' not found in the vector file.")
        return
        
    # Get raster information (SRS, resolution, extent, size, NoData, etc.) from the reference raster
    raster_info = get_raster_info(reference_raster)
    
    # Extract values from the dictionary returned by get_raster_info
    srs = raster_info['SRS']
    xres, yres = raster_info['Resolution']
    xmin, ymin, xmax, ymax = raster_info['Bounding Box']
    xsize, ysize = raster_info['Number of Pixels (x, y)']
    # Create the raster from the vector file using gdal_rasterize
    options = [
        "-a_srs", str(srs),          # SRS
        "-tr", str(xres), str(yres),  # Pixel resolution (xres, yres)
        "-te", str(xmin), str(ymin), str(xmax), str(ymax),  # Extent
        "-a", field_name,  # Attribute field name to use as burn value
        "-of", "GTiff",  # Output format (GeoTIFF)
        "-co", "COMPRESS=LZW"  # Apply LZW compression
    ]
    try:
        # Rasterize the vector file using the gdal_rasterize tool
        gdal.Rasterize(output_raster, input_vector, options=options)
        
        print(f"Rasterization successful! Output saved to: {output_raster}")
        
    except Exception as e:
        # If any error occurs, print an error message
        print(f"Error during rasterization: {e}")

def main():
    # Set up argument parsing for command-line execution
    parser = argparse.ArgumentParser(description="Rasterize a vector file using a reference raster.")
    parser.add_argument("input_vector", help="Path to the input vector file (e.g., Shapefile, GeoJSON).")
    parser.add_argument("field_name", help="The name of the attribute field to use as the burn value.")
    parser.add_argument("reference_raster", help="Path to the reference raster file (e.g., GeoTIFF).")
    parser.add_argument("output_raster", help="Path to the output raster file (e.g., GeoTIFF).")
        
    # Parse the arguments
    args = parser.parse_args()
    
    # Call the rasterization function
    rasterize_vector_using_field_name_and_ref_raster(args.input_vector, args.field_name, args.reference_raster, args.output_raster)

if __name__ == "__main__":
    main()
