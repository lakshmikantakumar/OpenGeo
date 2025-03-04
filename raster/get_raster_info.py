import argparse
import rasterio

def get_raster_info(raster_file):
    # Open the raster file using rasterio
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
    print(f"Number of Bands: {raster_info['Number of Bands']}")

if __name__ == "__main__":
    main()
