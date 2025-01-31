import argparse
import rasterio
import numpy as np

def calculate_category_area(raster_path):
    """
    Calculate the number of unique categories, their counts, and areas based on the raster data.
    
    Parameters:
        raster_path (str): Path to the raster file (e.g., GeoTIFF).
    
    Returns:
        dict: A dictionary with category values as keys and (count, area) as values.
    """
    
    # Open the raster file using rasterio
    with rasterio.open(raster_path) as src:
        # Get the resolution from the raster's metadata (pixel size)
        pixel_width, pixel_height = src.res[0], src.res[1]
        
        # Read the raster data (assuming single band raster)
        data = src.read(1)
        
        # Flatten the data to a 1D array for counting unique values
        unique_values, counts = np.unique(data, return_counts=True)
        
        # Create a dictionary to store the category count
        category_count = dict(zip(unique_values, counts))
        
        # Calculate the area for each category
        category_area = {category: count * abs(pixel_width) * abs(pixel_height) 
                         for category, count in category_count.items()}
        
    # Combine the category count and area into the result
    result = {}
    for category in category_count:
        result[category] = {
            'count': category_count[category],
            'area': category_area[category]
        }
    
    return result

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Calculate category counts and areas from a raster file.")
    parser.add_argument('raster_path', type=str, help="Path to the raster file (e.g., GeoTIFF).")
    return parser.parse_args()

def main():
    # Parse the command-line arguments
    args = parse_args()
    
    # Call the function with the provided raster path
    result = calculate_category_area(args.raster_path)
    
    # Output the result
    for category, data in result.items():
        print(f"Category: {category}")
        print(f"  Count: {data['count']}")
        print(f"  Area: {data['area']} square units")
        
if __name__ == "__main__":
    main()
