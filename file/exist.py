import os
from vector.get_vector_fields import get_field_names_and_types

def check_field_exists(input_vector, field_name):
    """
    Check if the attribute exists in the vector file.
    
    Parameters:
    - input_vector: Path to the input vector file (e.g., Shapefile, GeoJSON).
    - field_name: The name of the attribute field to check for existence.
    
    Returns:
    - True if the attribute exists, False otherwise.
    """
    fields = get_field_names_and_types(input_vector)
    for field_name, _ in fields:
        if field_name == field_name:
            return True
    return False

def check_file_exists(file_path):
    """
    Check if the given file exists.
    
    Parameters:
    - file_path: Path to the file.
    
    Returns:
    - True if the file exists, False otherwise.
    """
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return False
    return True
