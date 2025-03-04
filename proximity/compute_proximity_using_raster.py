import argparse
from osgeo import gdal

def compute_proximity(input_raster, output_raster, nodata_value):
    """
    Computes the proximity raster using GDAL's ComputeProximity() utility.

    :param input_raster: Path to the input raster file.
    :param output_raster: Path to save the output proximity raster.
    :param nodata_value: NoData value to set in the output raster.
    """
    gdal.UseExceptions()  # Enable GDAL exception handling

    # Open input raster
    ds = gdal.Open(input_raster, gdal.GA_ReadOnly)
    if ds is None:
        raise RuntimeError(f"Failed to open input raster: {input_raster}")

    # Get raster band
    band = ds.GetRasterBand(1)

    # Get spatial reference and geotransform from input
    proj = ds.GetProjection()    # Extracts the SRS (Spatial Reference System)
    geotransform = ds.GetGeoTransform()  # Extracts geotransform (location info)

    # Create output raster dataset with LZW compression
    driver = gdal.GetDriverByName("GTiff")
    out_ds = driver.Create(
        output_raster, 
        ds.RasterXSize, ds.RasterYSize, 1, 
        gdal.GDT_Float32, 
        options=["COMPRESS=LZW"]  # Apply LZW compression
    )

    if out_ds is None:
        raise RuntimeError(f"Failed to create output raster: {output_raster}")

    # Set projection and geotransform to match input raster
    out_ds.SetProjection(proj)
    out_ds.SetGeoTransform(geotransform)

    # Set NoData value for the output raster
    out_band = out_ds.GetRasterBand(1)
    out_band.SetNoDataValue(nodata_value)

    # Compute proximity using only necessary options
    # Define GDAL options
    options = ["NODATA=" + str(nodata_value), "DISTUNITS=GEO"]

    gdal.ComputeProximity(band, out_band, options)

    # Close datasets
    ds = None
    out_ds = None

    print(f"Proximity raster saved successfully: {output_raster}")

def main():
    """
    Main function to parse command-line arguments and run proximity computation.
    """
    parser = argparse.ArgumentParser(description="Compute proximity raster using GDAL")

    parser.add_argument("input_raster", type=str, help="Path to input raster file (GeoTIFF format)")
    parser.add_argument("output_raster", type=str, help="Path for saving the output proximity raster")
    parser.add_argument("--nodata", type=int, default=-9999, help="NoData value for the output raster")

    args = parser.parse_args()

    compute_proximity(args.input_raster, args.output_raster, args.nodata)

if __name__ == "__main__":
    main()
