import os
import zipfile
import argparse

def find_corrupted_zip_files(directory):
    """
    This function checks all ZIP files in a given directory to identify corrupted ones.
    
    Args:
    directory (str): Path to the directory containing ZIP files.

    Returns:
    list: A list of file paths that are corrupted or invalid ZIP files.
    """
    corrupted_files = []

    # Iterate over each file in the specified directory
    for filename in os.listdir(directory):
        # Check if the file is a ZIP file (case insensitive)
        if filename.lower().endswith('.zip'):
            file_path = os.path.join(directory, filename)

            try:
                # Try to open the ZIP file and perform a test on its contents
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    # Use testzip() to check for corruption
                    zip_ref.testzip()
            except zipfile.BadZipFile:
                # Catch bad ZIP file errors and add the file to the corrupted list
                print(f"BadZipFile: {file_path}")
                corrupted_files.append(file_path)
            except Exception as e:
                # Catch other errors and add the file to the corrupted list
                print(f"Error with file {file_path}: {e}")
                corrupted_files.append(file_path)

    return corrupted_files

def main():
    """
    Main function to parse command line arguments and call the find_corrupted_zip_files function.
    """
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Find corrupted ZIP files in a directory.")
    parser.add_argument("directory", help="The path to the directory containing ZIP files.")
    
    # Parse the command line arguments
    args = parser.parse_args()

    # Find corrupted files
    corrupted_files = find_corrupted_zip_files(args.directory)

    # Output the list of corrupted files
    if corrupted_files:
        print("\nCorrupted or invalid ZIP files:")
        for file in corrupted_files:
            print(file)
    else:
        print("\nNo corrupted or invalid ZIP files found.")

if __name__ == "__main__":
    # Call the main function to execute the script
    main()
