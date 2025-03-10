import argparse
import fiona
import shapely.geometry
from fiona.crs import from_epsg

def buffer_vector(input_vector, output_vector, buffer_distance):
    """
    Reads a vector file, applies a buffer to its geometries, and saves the result.

    :param input_vector: Path to the input vector file
    :param output_vector: Path to save the buffered vector file
    :param buffer_distance: Buffer distance in the CRS units of input vector
    """
    # Step 1: Read input features into a list
    features = []
    with fiona.open(input_vector, "r") as source:
        meta = source.meta.copy()  # Copy metadata
        meta["schema"]["geometry"] = "Polygon"  # Buffers create polygons
        
        for feature in source:
            geom = shapely.geometry.shape(feature["geometry"])  # Convert to Shapely geometry
            buffered_geom = geom.buffer(buffer_distance)  # Apply buffer
            
            # Create a new feature dictionary
            new_feature = {
                "type": "Feature",
                "geometry": shapely.geometry.mapping(buffered_geom),  # Convert back to GeoJSON-like format
                "properties": feature["properties"],  # Preserve attributes
            }
            features.append(new_feature)  # Store in list

    # Step 2: Write buffered features to a new file
    with fiona.open(output_vector, "w", **meta) as sink:
        sink.writerecords(features)  # Write all at once (avoids immutability issues)

    print(f"Buffered shapefile saved as: {output_vector}")

def main():
    parser = argparse.ArgumentParser(description="Apply buffer to vector geometries using Fiona and Shapely.")
    parser.add_argument("input_vector", help="Path to the input vector file (e.g., Shapefile or GeoJSON)")
    parser.add_argument("output_vector", help="Path to save the buffered vector file")
    parser.add_argument("buffer_distance", type=float, help="Buffer distance in the CRS units of input vector")

    args = parser.parse_args()
    
    buffer_vector(args.input_vector, args.output_vector, args.buffer_distance)

if __name__ == "__main__":
    main()
