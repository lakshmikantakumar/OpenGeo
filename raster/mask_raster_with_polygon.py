import argparse
import rasterio
from rasterio.mask import mask
from rasterio.warp import transform_geom
from rasterio.features import geometry_mask
import fiona
from shapely.geometry import mapping, shape
from rasterio.windows import Window
import numpy as np
import re

# Function to mask a raster with a polygon
def mask_raster_with_polygon(raster_path, polygon_path, output_path):
    """
    Masks a raster with a polygon, setting values outside the polygon to NoData.

    :param raster_path: Path to the input raster file.
    :param polygon_path: Path to the polygon shapefile.
    :param output_path: Path to save the masked raster.
    """
    # Open the raster file
    with rasterio.open(raster_path) as src:
        raster_crs = src.crs

        # Determine the nodata value and data type
        if src.nodata is not None:
            nodata_value = src.nodata
        else:
            nodata_value = -9999  # Set NoData to -9999 if not already set

        # If NoData is not set, adjust the dtype for unsigned types
        if src.nodata is None:
            # Get the dtype from the raster metadata
            dtype = src.dtypes[0]
            
            # Check if the dtype is unsigned (e.g., uint8, uint16, uint32)
            if np.issubdtype(np.dtype(dtype), np.unsignedinteger):  # Check if it's an unsigned integer
                # Extract the bit size using a regular expression to capture digits after 'uint'
                bit_size = int(re.search(r'\d+', dtype).group())  # Extracts the number after 'uint'
                
                # Convert to the corresponding signed integer type
                if bit_size == 8:
                    dtype = 'int16'  # uint8 -> int16
                elif bit_size == 16:
                    dtype = 'int32'  # uint16 -> int32
                elif bit_size == 32:
                    dtype = 'int64'  # uint32 -> int64
                else:
                    raise ValueError(f"Unsupported unsigned integer bit size: {bit_size}")
            elif np.issubdtype(np.dtype(dtype), np.signedinteger):
                # Keep the signed type as it is
                dtype = dtype
            elif np.issubdtype(np.dtype(dtype), np.floating):
                dtype = 'float32'  # For float types, we keep it as float32 for consistency
            else:
                raise ValueError(f"Unsupported data type: {dtype}")

        # Read the polygon shapefile
        with fiona.open(polygon_path, "r") as shapefile:
            shapefile_crs = shapefile.crs

            # Check if CRS matches and reproject if needed
            if raster_crs != shapefile_crs:
                print("Warning: CRS of shapefile and raster do not match. Reprojecting shapefile to raster CRS.")
                geometries = [
                    transform_geom(shapefile_crs, raster_crs, feature["geometry"])
                    for feature in shapefile
                ]
            else:
                geometries = [shape(feature["geometry"]) for feature in shapefile]

        # Create an output raster with the correct data type and nodata value
        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": src.height,
            "width": src.width,
            "transform": src.transform,
            "nodata": nodata_value,
            "dtype": dtype,  # Update data type to the appropriate signed type
            "compress": "LZW"  # Add LZW compression
        })

        # Create the new output raster
        with rasterio.open(output_path, "w", **out_meta) as dest:
            # Process the raster in windows to handle large files
            for ji, window in src.block_windows():
                # Read the data for the current window
                src_data = src.read(window=window)

                # Convert src_data to the appropriate signed dtype if it's unsigned
                if np.issubdtype(src_data.dtype, np.unsignedinteger):
                    src_data = src_data.astype(dtype)  # Convert to the new signed type

                # Create a mask for the current window
                window_transform = src.window_transform(window)
                mask = geometry_mask(
                    [mapping(geom) for geom in geometries],
                    out_shape=(src_data.shape[1], src_data.shape[2]),
                    transform=window_transform,
                    invert=True
                )

                # Apply the mask
                for band in range(src_data.shape[0]):
                    src_data[band][~mask] = nodata_value

                # Write the masked data to the output raster
                dest.write(src_data, window=window)

# Command-line argument parsing
def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Mask a raster with a polygon.")
    
    # Define command-line arguments with variable names
    parser.add_argument("--input_raster", type=str, required=True, help="Path to input raster file in TIFF format.")
    parser.add_argument("--input_polygon", type=str, required=True, help="Path to input polygon shapefile.")
    parser.add_argument("--output_raster", type=str, required=True, help="Path to output raster file in TIFF format.")
    
    return parser.parse_args()

def main():
    # Parse the command-line arguments
    args = parse_args()

    # Call the function with arguments passed from the command line
    mask_raster_with_polygon(args.input_raster, args.input_polygon, args.output_raster)
    
if __name__ == "__main__":
    main()