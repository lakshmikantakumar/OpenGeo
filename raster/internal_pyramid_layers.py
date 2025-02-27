import os
import warnings
import argparse
from osgeo import gdal

def convert_to_bigtiff(input_tif, output_tif):
    """
    Convert the input TIFF file to a BigTIFF format with DEFLATE compression.
    """
    options = ['COMPRESS=DEFLATE', 'BIGTIFF=YES']
    gdal.Translate(output_tif, input_tif, creationOptions=options)

def build_overviews_blockwise(input_tif):
    """
    Build overviews (pyramids) for the input TIFF file using block-wise processing.
    Compresses the overviews with LZW compression.
    """
    # Open the dataset in read mode
    ds = gdal.Open(input_tif, gdal.GA_Update)
    if ds is None:
        raise RuntimeError(f"Failed to open {input_tif}.")

    # Get the image dimensions and block size
    x_size = ds.RasterXSize
    y_size = ds.RasterYSize
    block_size_x = 256  # Block size in the x-direction
    block_size_y = 256  # Block size in the y-direction

    # Iterate through blocks in the image
    for y in range(0, y_size, block_size_y):
        for x in range(0, x_size, block_size_x):
            # Define the block size and read the block
            x_end = min(x + block_size_x, x_size)
            y_end = min(y + block_size_y, y_size)
            block = ds.ReadAsArray(x, y, x_end - x, y_end - y)

            # Optionally, perform processing on the block here (e.g., resampling)
            # For simplicity, we're just reading the block

    # Build overviews after processing blocks
    gdal.SetConfigOption('COMPRESS_OVERVIEW', 'lzw')
    ds.BuildOverviews('NEAREST', [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024])

    del ds  # Close the dataset

def internal_pyramids(tif_file):
    """
    Process a single TIFF file: convert to BigTIFF and build overviews with block-wise processing.
    """
    print(f"Processing {tif_file}...")
    output_file = os.path.splitext(tif_file)[0] + '_InterPyrd.tif'
    convert_to_bigtiff(tif_file, output_file)
    build_overviews_blockwise(output_file)
    # os.remove(output_file)  # Uncomment to remove temporary processed file after building overviews

def main():
    """
    Main function to handle command-line arguments and initiate processing.
    """
    # Suppress FutureWarning about GDAL exceptions not being explicitly set
    warnings.filterwarnings("ignore", category=FutureWarning)

    # Create argument parser
    parser = argparse.ArgumentParser(description="Process a TIFF file: convert to BigTIFF and build overviews with block-wise processing.")

    # Define the command-line argument for input TIFF file
    parser.add_argument('input_file', metavar='INPUT_FILE', type=str, 
                        help="Path to the input TIFF file to process")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Check if the input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: The file '{args.input_file}' does not exist.")
    else:
        # Process the provided TIFF file
        internal_pyramids(args.input_file)
        print("Processing completed.")

if __name__ == "__main__":
    # Run the main function if this script is executed
    main()
