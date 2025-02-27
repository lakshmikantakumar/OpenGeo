import os
import rasterio
import numpy as np
import argparse  # To handle command-line arguments


def normalize(array, input_min, input_max):
    """Normalize the array to the range 0-255."""
    # Apply the normalization formula
    normalized_array = (array - input_min) * (255.0 / (input_max - input_min))
    return normalized_array.astype(np.uint8)


def convert_to_8bit(input_path, output_path):
    """
    Convert a multi-band GeoTIFF image from 16-bit (or higher) to 8-bit.
    
    Parameters:
    - input_path: Path to the input GeoTIFF file.
    - output_path: Path where the output 8-bit GeoTIFF file will be saved.
    """
    
    with rasterio.open(input_path) as src:
        # Initialize arrays to store min and max for each band
        band_mins = []
        band_maxs = []

        # Compute the global min and max for each band
        for band in range(1, src.count + 1):
            band_data = src.read(band)
            band_mins.append(band_data.min())  # Store the min value for the band
            band_maxs.append(band_data.max())  # Store the max value for the band

        # Get the block shape of the raster (i.e., how big each block is)
        block_shape = src.block_shapes[0]  # Assuming all bands have the same block size

        # Define the metadata for the new dataset
        kwargs = src.meta
        kwargs.update(
            dtype=rasterio.uint8,  # Output format: 8-bit unsigned integer
            count=src.count,  # Number of bands in the input raster
            compress='lzw',  # Apply LZW compression for file size reduction
            BIGTIFF='YES'  # Enable BigTIFF for large files
        )

        # Open the output file in write mode
        with rasterio.open(output_path, 'w', **kwargs) as dst:
            # Loop through each block in the raster
            for i in range(0, src.height, block_shape[0]):
                for j in range(0, src.width, block_shape[1]):
                    # Ensure the window does not go beyond the raster's dimensions
                    window_height = min(block_shape[0], src.height - i)
                    window_width = min(block_shape[1], src.width - j)

                    # Read the block for all bands
                    window = rasterio.windows.Window(j, i, window_width, window_height)
                    data_block = src.read(window=window)

                    # Normalize each band using its precomputed min and max
                    data_8bit_block = np.zeros_like(data_block, dtype=np.uint8)
                    for band in range(data_block.shape[0]):
                        band_data = data_block[band]
                        band_min = band_mins[band]  # Use the precomputed min value
                        band_max = band_maxs[band]  # Use the precomputed max value
                        data_8bit_block[band] = normalize(band_data, band_min, band_max)

                    # Write the normalized block to the output file
                    dst.write(data_8bit_block, window=window, indexes=range(1, data_block.shape[0] + 1))

def main():
    """
    Main function to parse command-line arguments and execute the conversion.
    """
    # Initialize argument parser
    parser = argparse.ArgumentParser(description="Convert a multi-band GeoTIFF image to 8-bit")
    
    # Add arguments for input and output paths
    parser.add_argument('input_file', type=str, help="Path to the input GeoTIFF file")
    parser.add_argument('output_file', type=str, help="Path to save the output 8-bit GeoTIFF file")
    
    # Parse the command-line arguments
    args = parser.parse_args()
    
    # Call the conversion function with the provided input and output file paths
    convert_to_8bit(args.input_file, args.output_file)
    print(f"Conversion complete! Output saved to {args.output_file}")


if __name__ == '__main__':
    # Run the main function when the script is executed from the command line
    main()
