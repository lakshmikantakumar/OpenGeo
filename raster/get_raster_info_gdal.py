import argparse
from osgeo import gdal, osr

def get_raster_info_gdal(raster_file):
    """
    Retrieve raster information using GDAL including SRS, resolution, bounds, pixel size, NoData, dtype, and bands.
    """
    ds = gdal.Open(raster_file, gdal.GA_ReadOnly)
    if ds is None:
        raise FileNotFoundError(f"Raster file not found: {raster_file}")

    # Get geotransform to calculate resolution and bounding box
    gt = ds.GetGeoTransform()
    xres = gt[1]  # pixel width
    yres = -gt[5]  # pixel height (negative because origin is top-left)
    xmin = gt[0]
    ymax = gt[3]
    xmax = xmin + xres * ds.RasterXSize
    ymin = ymax - yres * ds.RasterYSize

    # Spatial reference using OSR
    srs = osr.SpatialReference(wkt=ds.GetProjection())
    epsg = srs.GetAttrValue('AUTHORITY', 1)  # Get EPSG code
    srs_wkt = srs.ExportToWkt()  # Export to WKT

    # Number of pixels (dimensions)
    xsize, ysize = ds.RasterXSize, ds.RasterYSize
    
    # Number of bands
    nband = ds.RasterCount

    # Data type mapping from GDAL data types to theoretical ranges
    dtype_mapping = {
        gdal.GDT_Byte:   ("uint8", 8, 0, 255),
        gdal.GDT_Int16:  ("int16", 16, -32768, 32767),
        gdal.GDT_UInt16: ("uint16", 16, 0, 65535),
        gdal.GDT_Int32:  ("int32", 32, -2147483648, 2147483647),
        gdal.GDT_UInt32: ("uint32", 32, 0, 4294967295),
        gdal.GDT_Float32:("float32", 32, -3.4e38, 3.4e38),
        gdal.GDT_Float64:("float64", 64, -1.7e308, 1.7e308)
    }

    # For simplicity, assume all bands have the same type
    band = ds.GetRasterBand(1)
    dtype = band.DataType
    data_type, bit_depth, bit_min_val, bit_max_val = dtype_mapping.get(dtype, (None, None, None, None))
    
    if data_type is None:
        raise ValueError(f"Unsupported GDAL data type: {dtype}")
    
    # Get NoData value from the first band
    nodata = band.GetNoDataValue()

    # Return as dictionary
    return {
        'SRS': epsg,
        'Resolution': (xres, yres),
        'Bounding Box': (xmin, ymin, xmax, ymax),
        'Number of Pixels (x, y)': (xsize, ysize),
        'NoData': nodata,
        'Data Type': data_type,
        'Bit Depth': bit_depth,
        'Bit Min Value': bit_min_val,
        'Bit Max Value': bit_max_val,
        'Number of Bands': nband
    }


def main():
    # Setting up argument parsing
    parser = argparse.ArgumentParser(description="Extract raster information such as SRS, resolution, bounds, pixel size, NoData, and dtype.")
    
    # Argument for raster file input
    parser.add_argument('raster_file', type=str, help='Path to the raster file (e.g., .tif)')
    
    # Parse the arguments from the command line
    args = parser.parse_args()
    
    # Get raster information by calling the function
    raster_info = get_raster_info_gdal(args.raster_file)
    
    # Print out the results
    print(f"SRS: {raster_info['SRS']}")
    print(f"Resolution (Pixel Size in Map Units): {raster_info['Resolution']}")
    print(f"Bounding Box (xmin, ymin, xmax, ymax): {raster_info['Bounding Box']}")
    print(f"Number of Pixels (xsize, ysize): {raster_info['Number of Pixels (x, y)']}")
    print(f"NoData Value: {raster_info['NoData']}")
    print(f"Data Type: {raster_info['Data Type']}")
    print(f"Bit Depth: {raster_info['Bit Depth']}")
    print(f"Bit Min Value: {raster_info['Bit Min Value']}")
    print(f"Bit Max Value: {raster_info['Bit Max Value']}")
    print(f"Number of Bands: {raster_info['Number of Bands']}")


if __name__ == "__main__":
    main()
