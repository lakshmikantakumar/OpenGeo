import argparse
import rasterio
import numpy as np
from rasterio.windows import Window
from rasterio.errors import RasterioIOError

def replace_pixel_value(input_tif_source, input_tif_reference, output_tif, value_to_replace, 
                        tile_size=1024, band=1, compress='LZW'):
    """
    Replaces the specified pixel value in the source GeoTIFF file with corresponding pixel values 
    from the reference GeoTIFF file and writes the result to the output GeoTIFF file with compression.
    
    Parameters:
    - input_tif_source: str, Path to the source GeoTIFF file (with values to be replaced)
    - input_tif_reference: str, Path to the reference GeoTIFF file (from which pixel values are taken)
    - output_tif: str, Path to save the output GeoTIFF file
    - value_to_replace: int, The pixel value(s) to be replaced (e.g., 2 for Nodata)
    - tile_size: int, Size of the tile (in pixels, both width and height) to process at once (default is 1024)
    - band: int, Band number to be used for processing (default is 1)
    - compress: str, Compression format to use for the output file (default is 'LZW')
    """
    try:
        # Open the source and reference GeoTIFF files
        with rasterio.open(input_tif_source) as src1, rasterio.open(input_tif_reference) as src2:
            
            # Check if both files have the same shape and CRS
            if src1.shape != src2.shape:
                raise ValueError("Input files do not have the same dimensions!")
            if src1.crs != src2.crs:
                raise ValueError("Input files do not have the same CRS!")

            # Create the output raster with specified compression
            with rasterio.open(output_tif, 'w', driver='GTiff', 
                               count=1, dtype=src1.dtypes[0], crs=src1.crs, 
                               transform=src1.transform, width=src1.width, 
                               height=src1.height, compress=compress) as dst:
                
                # Iterate over the raster in tiles
                for i in range(0, src1.height, tile_size):
                    for j in range(0, src1.width, tile_size):
                        # Define the window (tile) to read and process
                        window = Window(j, i, min(tile_size, src1.width - j), min(tile_size, src1.height - i))
                        
                        # Read the source and reference data for the current tile
                        data_source = src1.read(band, window=window)
                        data_reference = src2.read(band, window=window)
                        
                        # Handle single or list value for value_to_replace
                        replace_mask = data_source == value_to_replace
                        
                        # Replace the specified value in source raster with corresponding values from the reference raster
                        data_source[replace_mask] = data_reference[replace_mask]
                        
                        # Write the modified data to the output raster for the current tile
                        dst.write(data_source, band, window=window)
        
        print(f"Processing complete! The output has been saved to {output_tif} with {compress} compression.")
    
    except RasterioIOError as e:
        print(f"Error opening raster files: {e}")
    
    except ValueError as e:
        print(f"Error: {e}")
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def parse_args():
    """
    Parse command-line arguments using argparse.
    
    Returns:
    argparse.Namespace: The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Replace pixel values in a source GeoTIFF with values from a reference GeoTIFF.")
    
    # Adding arguments
    parser.add_argument('input_tif_source', type=str, help="Path to the source GeoTIFF file (with values to be replaced)")
    parser.add_argument('input_tif_reference', type=str, help="Path to the reference GeoTIFF file (from which pixel values are taken)")
    parser.add_argument('output_tif', type=str, help="Path to save the output GeoTIFF file")
    parser.add_argument('value_to_replace', type=int, help="The pixel value(s) to be replaced in the source raster")
    parser.add_argument('--tile_size', type=int, default=1024, help="Size of the tile to process at once (default is 1024)")
    parser.add_argument('--band', type=int, default=1, help="Band number to be processed (default is 1)")
    parser.add_argument('--compress', type=str, default='LZW', help="Compression method for the output file (default is 'LZW')")
    
    return parser.parse_args()

def main():
    """
    Main function to handle command-line execution.
    """
    # Parse arguments
    args = parse_args()

    # Call the function to replace pixel values
    replace_pixel_value(
        input_tif_source=args.input_tif_source,
        input_tif_reference=args.input_tif_reference,
        output_tif=args.output_tif,
        value_to_replace=args.value_to_replace,
        tile_size=args.tile_size,
        band=args.band,
        compress=args.compress
    )

if __name__ == '__main__':
    main()
