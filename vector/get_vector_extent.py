import os
import argparse
from osgeo import ogr

def get_vector_extent(input_vector):
    """
    Get the bounding box (extent) of the vector file.
    
    Parameters:
    - input_vector: Path to the input vector file (e.g., Shapefile, GeoJSON).
    
    Returns:
    - The bounding box as (xmin, ymin, xmax, ymax).
    """
    # Use appropriate driver based on file type (Shapefile or GeoJSON)
    if input_vector.endswith('.shp'):
        driver = ogr.GetDriverByName('ESRI Shapefile')
    elif input_vector.endswith('.geojson'):
        driver = ogr.GetDriverByName('GeoJSON')
    else:
        raise ValueError("Unsupported file format. Only Shapefile (.shp) and GeoJSON (.geojson) are supported.")
    
    datasource = driver.Open(input_vector, 0)
    
    if not datasource:
        raise ValueError(f"Failed to open vector file: {input_vector}")
    
    layer = datasource.GetLayer()
    extent = layer.GetExtent()  # Returns (xmin, ymin, xmax, ymax)
    return extent

def main():
    # Set up argument parsing for command-line execution
    parser = argparse.ArgumentParser(description="Get the bounding box (extent) of a vector file.")
    parser.add_argument("input_vector", help="Path to the input vector file (e.g., Shapefile, GeoJSON).")
    
    # Parse the arguments
    args = parser.parse_args()

    # Check if the input file exists
    if not os.path.exists(args.input_vector):
        print(f"Error: The file '{args.input_vector}' does not exist.")
        return

    try:
        # Get the extent of the vector file
        extent = get_vector_extent(args.input_vector)
        print(f"Bounding Box (Extent) of '{args.input_vector}':")
        print(f"  xmin: {extent[0]}")
        print(f"  ymin: {extent[1]}")
        print(f"  xmax: {extent[2]}")
        print(f"  ymax: {extent[3]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
