import os
import argparse
from osgeo import gdal, ogr
import numpy as np

def buffer_raster(input_raster, output_raster, buffer_distance):
    """
    Buffer a raster by a specified distance.

    Parameters:
    - input_raster: Path to the input raster file (GeoTIFF).
    - output_raster: Path to the output buffered raster file.
    - buffer_distance: The distance to buffer in map units.
    """
    # Open the input raster
    ds = gdal.Open(input_raster)
    if ds is None:
        raise ValueError(f"Failed to open raster file: {input_raster}")
    
    # Get the raster's spatial reference and transform
    geotransform = ds.GetGeoTransform()
    projection = ds.GetProjection()

    # Get the raster's array (values)
    raster_array = ds.ReadAsArray()

    # Calculate the buffer size in pixels (buffer distance divided by pixel size)
    pixel_size_x = geotransform[1]  # Pixel size in x-direction (longitude)
    pixel_size_y = geotransform[5]  # Pixel size in y-direction (latitude)
    
    buffer_pixels_x = int(buffer_distance / abs(pixel_size_x))  # Convert buffer to pixels (x)
    buffer_pixels_y = int(buffer_distance / abs(pixel_size_y))  # Convert buffer to pixels (y)

    # Create a mask (1 for buffered areas, 0 for non-buffered areas)
    height, width = raster_array.shape
    mask = np.zeros((height, width), dtype=np.uint8)

    # Mark the buffered area with 1s
    for i in range(height):
        for j in range(width):
            if raster_array[i, j] > 0:  # Consider non-zero values as "valid"
                min_x = max(0, j - buffer_pixels_x)
                max_x = min(width - 1, j + buffer_pixels_x)
                min_y = max(0, i - buffer_pixels_y)
                max_y = min(height - 1, i + buffer_pixels_y)

                mask[min_y:max_y+1, min_x:max_x+1] = 1

    # Create the output raster with the same projection, transform, and size as the input raster
    driver = gdal.GetDriverByName('GTiff')
    if driver is None:
        raise ValueError("GDAL driver for GeoTIFF not available")
    
    output_ds = driver.Create(output_raster, width, height, 1, gdal.GDT_Byte)
    output_ds.SetProjection(projection)
    output_ds.SetGeoTransform(geotransform)

    # Write the mask array to the output raster
    output_ds.GetRasterBand(1).WriteArray(mask)

    # Set NoData value to 0
    output_ds.GetRasterBand(1).SetNoDataValue(0)

    # Close the datasets
    ds = None
    output_ds = None

    print(f"Buffering completed. Output saved to: {output_raster}")

def main():
    # Set up argument parsing for command-line execution
    parser = argparse.ArgumentParser(description="Buffer a raster by a specified distance.")
    parser.add_argument("input_raster", help="Path to the input raster file (e.g., GeoTIFF).")
    parser.add_argument("output_raster", help="Path to the output raster file (e.g., GeoTIFF).")
    parser.add_argument("buffer_distance", type=float, help="The buffer distance in map units.")

    # Parse the arguments
    args = parser.parse_args()

    # Check if the input file exists
    if not os.path.exists(args.input_raster):
        print(f"Error: The file '{args.input_raster}' does not exist.")
        return

    try:
        # Call the raster buffering function
        buffer_raster(args.input_raster, args.output_raster, args.buffer_distance)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
