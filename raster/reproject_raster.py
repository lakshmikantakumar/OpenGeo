import argparse
import os
from osgeo import gdal, osr

def get_wkt_from_epsg(epsg_code):
    """Convert EPSG code to WKT format."""
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(int(epsg_code.split(":")[1]))  # Extract numeric part
    return srs.ExportToWkt()

def reproject_raster(input_raster, output_raster, target_crs):
    """
    Reprojects a raster to a specified coordinate reference system (CRS).
    
    Parameters:
        input_raster (str): Path to the input raster file.
        output_raster (str): Path to save the reprojected raster.
        target_crs (str): Target coordinate reference system in EPSG format (e.g., 'EPSG:4326').
    """
    # Check if input raster exists
    if not os.path.isfile(input_raster):
        raise FileNotFoundError(f"Error: Input raster file '{input_raster}' not found.")
    
    # Open the input raster
    src_ds = gdal.Open(input_raster)
    if src_ds is None:
        raise RuntimeError(f"Error: Unable to open raster '{input_raster}'. Ensure it is a valid raster file.")
    
    # Convert EPSG to WKT format
    target_wkt = get_wkt_from_epsg(target_crs)
    print(f"DEBUG: Converted WKT CRS -> '{target_wkt}'")
    
    # Perform reprojection using gdal.Warp
    print(f"Running gdal.Warp with parameters: input={input_raster}, output={output_raster}, dstSRS='{target_wkt}'")
    gdal.Warp(output_raster, src_ds, dstSRS=target_wkt)
    
    # Close dataset
    src_ds = None
    print(f"Reprojection completed. Output saved at: {output_raster}")

def main():
    """ Parses command-line arguments and runs the reprojection function."""
    parser = argparse.ArgumentParser(
        description="Reproject a raster to a specified coordinate reference system (CRS) using GDAL."
    )
    parser.add_argument("input_raster", type=str, help="Path to the input raster file.")
    parser.add_argument("output_raster", type=str, help="Path to save the reprojected raster.")
    parser.add_argument("target_crs", type=str, help="Target CRS in EPSG format (e.g., 'EPSG:4326').")
    
    args = parser.parse_args()
    
    try:
        reproject_raster(args.input_raster, args.output_raster, args.target_crs)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()