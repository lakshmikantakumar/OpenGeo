import os
import argparse

def find_files_by_extension(root_path, extension, recursive=True):
    """
    This function searches through the specified root folder, and optionally its subfolders,
    to find all files that match the given extension.

    Args:
    root_path (str): The directory path where the search starts.
    extension (str): The file extension to search for (e.g., 'tiff', 'jpg', 'pdf').
    recursive (bool): Whether to search subfolders (default is True).
    
    Returns:
    list: A list containing the full paths of all files that match the extension.
    """
    
    # Ensure the extension starts with a dot (e.g., '.tiff'). If not, add it.
    if not extension.startswith('.'):
        extension = '.' + extension
    
    # Initialize an empty list to hold the paths of files that match the extension.
    matching_files = []
    
    # Use os.walk() if recursive search is required, otherwise use os.listdir()
    if recursive:
        # Use os.walk() to iterate through the directory structure (including subfolders)
        for foldername, subfolders, filenames in os.walk(root_path):
            for filename in filenames:
                if filename.lower().endswith(extension.lower()):
                    file_path = os.path.join(foldername, filename)
                    matching_files.append(file_path)
    else:
        # Only search the root folder (do not recurse into subdirectories)
        for filename in os.listdir(root_path):
            full_path = os.path.join(root_path, filename)
            if os.path.isfile(full_path) and filename.lower().endswith(extension.lower()):
                matching_files.append(full_path)
    
    # Return the list of file paths that matched the given extension.
    return matching_files

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Find files by extension in a root directory")
    parser.add_argument("root_path", help="The directory path where the search starts")
    parser.add_argument("extension", help="The file extension to search for (e.g., 'tiff', 'jpg', 'pdf')")
    parser.add_argument("--recursive", action="store_true", help="Search subdirectories recursively (default is True)")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Call the find_files_by_extension function
    result = find_files_by_extension(args.root_path, args.extension, recursive=args.recursive)
    
    # Print the result (list of matching files)
    if result:
        for file_path in result:
            print(file_path)
    else:
        print(f"No files with the '{args.extension}' extension were found.")

if __name__ == "__main__":
    main()
