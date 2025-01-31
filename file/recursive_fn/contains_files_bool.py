import argparse
from pathlib import Path
import fnmatch

def contains_files(path, pattern='*.tif', recursive=False, case_sensitive=True):
    """
    Checks if any files matching the given pattern exist in the specified folder.
    
    Args:
        path (str or Path): The folder path to search in.
        pattern (str): The pattern to match files (default is '*.tif').
        recursive (bool): Whether to search subdirectories recursively (default is False).
        case_sensitive (bool): Whether the search should be case sensitive (default is True).
    
    Returns:
        bool: True if matching files are found, False otherwise.
    """
    # Ensure the input path is a Path object
    p = Path(path)

    # Adjust the pattern based on case sensitivity
    if not case_sensitive:
        pattern = pattern.lower()

    # Check if we should recursively search through subdirectories
    if recursive:
        matching_files = [f for f in p.rglob('*') if fnmatch.fnmatch(f.name, pattern)]
    else:
        matching_files = [f for f in p.glob('*') if fnmatch.fnmatch(f.name, pattern)]

    # Return True if matching files are found, else False
    return bool(matching_files)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Check if files matching a pattern exist in a folder.")
    
    # Add arguments to the parser
    parser.add_argument('path', type=str, help="The folder path to search in.")
    parser.add_argument('--pattern', type=str, default='*.tif', help="The pattern to match files (default is '*.tif').")
    parser.add_argument('--recursive', action='store_true', help="Search subdirectories recursively.")
    parser.add_argument('--case-insensitive', action='store_false', help="Perform a case-insensitive search.")
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Call the contains_files function with the parsed arguments
    result = contains_files(args.path, pattern=args.pattern, recursive=args.recursive, case_sensitive=args.case_insensitive)
    
    # Print the result (True or False)
    if result:
        print(f"Matching files found in '{args.path}'")
    else:
        print(f"No matching files found in '{args.path}'")

if __name__ == '__main__':
    main()
