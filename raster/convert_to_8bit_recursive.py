import os
import argparse
from find_files_by_extension_in_root import find_files_by_extension
from convert_to_8bit import convert_to_8bit  

def process_tiff_files(input_folder, output_folder, extension='tif', recursive=True):
    """
    Process all files with the given extension in the input folder and convert them to 8-bit, saving them in the output folder.

    Args:
    input_folder (str): Path to the input folder containing the files.
    output_folder (str): Path to the output folder where the processed files will be saved.
    extension (str): File extension to look for (default is 'tiff').
    recursive (bool): Whether to search subdirectories (default is True).
    """
    # Find all files with the given extension in the input folder (and optionally subfolders)
    files_to_process = find_files_by_extension(input_folder, extension, recursive)
    
    for file_path in files_to_process:
        # Get the last folder name and file name
        last_folder_name = os.path.basename(os.path.dirname(file_path))
        file_name, file_ext = os.path.splitext(os.path.basename(file_path))
        
        # Construct the output file path
        output_file_name = f"{last_folder_name}_{file_name}_8bit{file_ext}"
        output_file_path = os.path.join(output_folder, output_file_name)

        # Convert the file to 8-bit and save it to the output folder
        print(f"Processing {file_path} -> {output_file_path}")
        convert_to_8bit(file_path, output_file_path)
    
    print("Processing complete!")

def main():
    # Setup the argument parser
    parser = argparse.ArgumentParser(description="Convert image files to 8-bit format.")
    
    # Add command-line arguments
    parser.add_argument('input_folder', type=str, help="Path to the input folder containing the files.")
    parser.add_argument('output_folder', type=str, help="Path to the output folder where the processed files will be saved.")
    parser.add_argument('--extension', type=str, default='tif', help="File extension to search for (default is 'tiff').")
    parser.add_argument('--recursive', type=bool, default=True, help="Whether to search subdirectories (default is True).")
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Call the process_tiff_files function with the provided arguments
    process_tiff_files(args.input_folder, args.output_folder, extension=args.extension, recursive=args.recursive)

if __name__ == '__main__':
    main()
