import argparse
import rasterio
import numpy as np

def get_raster_info(raster_file):
    """
    Retrieve comprehensive information about a raster file including spatial reference,
    bounding box, resolution, pixel size, and dtype information.

    Returns a dictionary with all the raster info.
    """
    with rasterio.open(raster_file) as src:
        # Get the Spatial Reference System (SRS)
        srs = src.crs
        
        # Get the raster's bounding box coordinates (xmin, ymin, xmax, ymax)
        bounds = src.bounds
        xmin, ymin, xmax, ymax = bounds
        
        # Get the resolution (pixel size) in map units
        xres, yres = src.res
        
        # Get the number of pixels in the x and y dimensions
        xsize, ysize = src.width, src.height
        
        # Get the NoData value (if any)
        nodata = src.nodata
        
        # Get the data type of the raster
        dtype = src.dtypes[0]
        
        # Map numpy/rasterio dtypes to theoretical ranges
        dtype_info = {
            "uint8":   (8, 0, 255),
            "int8":    (8, -128, 127),
            "uint16":  (16, 0, 65535),
            "int16":   (16, -32768, 32767),
            "uint32":  (32, 0, 4294967295),
            "int32":   (32, -2147483648, 2147483647),
            "float32": (32, -3.4e38, 3.4e38),
            "float64": (64, -1.7e308, 1.7e308)
        }
        
        # Get theoretical min/max and bit depth for the raster dtype
        bit_depth, bit_min_val, bit_max_val = dtype_info.get(dtype, (None, None, None))
        if bit_depth is None:
            raise ValueError(f"Unsupported raster dtype: {dtype}")

        # Get number of bands in raster
        nband = src.count
        
        # Return all the calculated values as a dictionary
        return {
            'SRS': srs,
            'Resolution': (xres, yres),
            'Bounding Box': (xmin, ymin, xmax, ymax),
            'Number of Pixels (x, y)': (xsize, ysize),
            'NoData': nodata,
            'Data Type': dtype,
            'Bit Depth': bit_depth,
            'Bit Min Value': bit_min_val,
            'Bit Max Value': bit_max_val,
            'Number of Bands': nband
        }

    
def main():
    # Setting up argument parsing
    parser = argparse.ArgumentParser(description="Extract raster information such as SRS, resolution, bounds, pixel size, NoData, and dtype.")
    
    # Argument for raster file input
    parser.add_argument('raster_file', type=str, help='Path to the raster file (e.g., .tif)')
    
    # Parse the arguments from the command line
    args = parser.parse_args()
    
    # Get raster information by calling the function
    raster_info = get_raster_info(args.raster_file)
    
    # Print out the results
    print(f"SRS: {raster_info['SRS']}")
    print(f"Resolution (Pixel Size in Map Units): {raster_info['Resolution']}")
    print(f"Bounding Box (xmin, ymin, xmax, ymax): {raster_info['Bounding Box']}")
    print(f"Number of Pixels (xsize, ysize): {raster_info['Number of Pixels (x, y)']}")
    print(f"NoData Value: {raster_info['NoData']}")
    print(f"Data Type: {raster_info['Data Type']}")
    print(f"Bit Depth: {raster_info['Bit Depth']}")
    print(f"Bit Min Value: {raster_info['Bit Min Value']}")
    print(f"Bit Max Value: {raster_info['Bit Max Value']}")
    print(f"Number of Bands: {raster_info['Number of Bands']}")


if __name__ == "__main__":
    main()
