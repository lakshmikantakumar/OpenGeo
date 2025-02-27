import os
import argparse
from find_files_by_extension_in_root import find_files_by_extension
from internal_pyramid_layers import internal_pyramids  

def process_tiff_files(input_folder, extension='tif', recursive=True):
    """
    Process all files with the given extension in the input folder and add internal pyramids, saving them in the output folder.

    Args:
    input_folder (str): Path to the input folder containing the files.
    extension (str): File extension to look for (default is 'tiff').
    recursive (bool): Whether to search subdirectories (default is True).
    """
    # Find all files with the given extension in the input folder (and optionally subfolders)
    files_to_process = find_files_by_extension(input_folder, extension, recursive)
    
    for file_path in files_to_process:
        # Convert the file to 8-bit and save it to the output folder
        # print(f"Processing {file_path}")
        internal_pyramids(file_path)
    
    print("Processing complete!")

def main():
    # Setup the argument parser
    parser = argparse.ArgumentParser(description="Adding internal pyramids to raster")
    
    # Add command-line arguments
    parser.add_argument('input_folder', type=str, help="Path to the input folder containing the files.")
    parser.add_argument('--extension', type=str, default='tif', help="File extension to search for (default is 'tiff').")
    parser.add_argument('--recursive', type=bool, default=True, help="Whether to search subdirectories (default is True).")
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Call the process_tiff_files function with the provided arguments
    process_tiff_files(args.input_folder, extension=args.extension, recursive=args.recursive)

if __name__ == '__main__':
    main()
