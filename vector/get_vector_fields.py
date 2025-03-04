import argparse
from osgeo import ogr

def get_field_names_and_types(input_vector):
    """
    Get the field names and their types from a vector file.
    
    Parameters:
    - input_vector: Path to the input vector file (e.g., Shapefile, GeoJSON).
    
    Returns:
    - List of tuples containing field name and field type.
    """
    # Open the vector file
    driver = ogr.GetDriverByName('ESRI Shapefile') if input_vector.endswith('.shp') else ogr.GetDriverByName('GeoJSON')
    datasource = ogr.Open(input_vector)
    
    if not datasource:
        raise Exception(f"Failed to open file: {input_vector}")
    
    # Get the layer from the datasource (assume first layer if multiple layers exist)
    layer = datasource.GetLayer()
    
    field_info = []
    
    # Iterate over the fields in the layer
    for i in range(layer.GetLayerDefn().GetFieldCount()):
        field_defn = layer.GetLayerDefn().GetFieldDefn(i)
        field_name = field_defn.GetName()
        field_type = field_defn.GetFieldTypeName(field_defn.GetType())
        field_info.append((field_name, field_type))
    
    # Close the datasource
    datasource = None
    
    return field_info

def main():
    # Set up argument parsing for command-line execution
    parser = argparse.ArgumentParser(description="Get field names and types from a vector file.")
    parser.add_argument("input_vector", help="Path to the input vector file (e.g., Shapefile, GeoJSON).")
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Get field names and types
    try:
        fields = get_field_names_and_types(args.input_vector)
        if fields:
            print("Field names and types:")
            for field_name, field_type in fields:
                print(f"{field_name}: {field_type}")
        else:
            print("No fields found in the vector file.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
