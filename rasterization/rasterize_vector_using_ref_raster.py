import os
import argparse
from osgeo import gdal
import rasterio
from raster.get_raster_info import get_raster_info
from file.exist import check_file_exists


def rasterize_vector_using_ref_raster(input_vector, reference_raster, output_raster):
    """
    Rasterize a vector file using the information from get_raster_info.py.
    
    Parameters:
    - input_vector: Path to the input vector file (Shapefile, GeoJSON, etc.)
    - reference_raster: Path to the reference raster file (e.g., GeoTIFF)
    - output_raster: Path to the output raster file (e.g., GeoTIFF)
    """
    # Check if the input files exist
    if not check_file_exists(input_vector) or not check_file_exists(reference_raster):
        return  # Stop execution if either file is missing
        
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
        #"-ts", str(xsize), str(ysize),  # Raster size (xsize, ysize)
        "-of", "GTiff",  # Output format (GeoTIFF)
        "-burn", "1",  # Burn value (you can change this to an attribute or custom value)
        "-co", "COMPRESS=LZW"  # Apply LZW compression
    ]
    try:
        # Rasterize the vector file using the gdal_rasterize tool
        gdal.Rasterize(output_raster, input_vector, options=options)       
        print(f"Rasterization successful! Output saved to: {output_raster}")
    
    except Exception as e:
        print(f"Error during rasterization: {e}")

def main():
    # Set up argument parsing for command-line execution
    parser = argparse.ArgumentParser(description="Rasterize a vector file using a reference raster.")
    parser.add_argument("input_vector", help="Path to the input vector file (e.g., Shapefile, GeoJSON).")
    parser.add_argument("reference_raster", help="Path to the reference raster file (e.g., GeoTIFF).")
    parser.add_argument("output_raster", help="Path to the output raster file (e.g., GeoTIFF).")
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Call the rasterization function
    rasterize_vector_using_ref_raster(args.input_vector, args.reference_raster, args.output_raster)

if __name__ == "__main__":
    main()
