import argparse
import os
from osgeo import gdal
from raster.get_raster_info import get_raster_info
from raster.resample_raster_gdal import resample_raster

def resample_raster_using_ref_raster(input_raster, reference_raster, output_raster, resample_alg="nearest"):
    """
    Resamples an input raster to match the spatial resolution and extent of a reference raster.

    Parameters:
        input_raster (str): Path to the input raster file.
        reference_raster (str): Path to the reference raster file (used for resolution & bounds).
        output_raster (str): Path where the resampled raster will be saved.
        resample_alg (str, optional): Resampling method. Default is 'nearest'.
                                      Options: 'nearest', 'bilinear', 'cubic', 'cubicspline', 
                                               'lanczos', 'average', 'mode'.
    """

    # Ensure input and reference rasters exist
    if not os.path.exists(input_raster):
        raise FileNotFoundError(f"Error: Input raster not found: {input_raster}")

    if not os.path.exists(reference_raster):
        raise FileNotFoundError(f"Error: Reference raster not found: {reference_raster}")

    # Retrieve raster metadata using get_raster_info function
    input_raster_info = get_raster_info(input_raster)
    ref_raster_info = get_raster_info(reference_raster)

    # Extract relevant values from reference raster
    ref_srs = ref_raster_info["SRS"]  # Projection system (SRS)
    ref_xres, ref_yres = ref_raster_info["Resolution"]  # Pixel size (resolution)
    ref_bounds = ref_raster_info["Bounding Box"]  # Bounding box (extent)

    # Extract input raster's projection
    input_srs = input_raster_info["SRS"]

    # Check if the input and reference raster projections match
    if input_srs != ref_srs:
        raise ValueError(
            f"Error: Spatial Reference System (SRS) mismatch detected!\n"
            f"Input Raster SRS: {input_srs}\nReference Raster SRS: {ref_srs}\n"
            "Please reproject the input raster before resampling."
        )

    # Display processing details
    print(f"\nResampling: {input_raster}")
    print(f"Reference Raster: {reference_raster}")
    print(f"Output Raster: {output_raster}")
    print(f"Resolution: {ref_xres} x {ref_yres}")
    print(f"Output Bounds: {ref_bounds}")
    print(f"Resampling Algorithm: {resample_alg}\n")

    # Call resample_raster function to perform resampling
    resample_raster(input_raster, output_raster, ref_xres, ref_yres, ref_bounds, resample_alg)

    print(f" Resampling completed successfully! Output saved at: {output_raster}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resamples a raster to match the resolution and extent of a reference raster.")
    parser.add_argument("input_raster", type=str, help="Path to the input raster file")
    parser.add_argument("reference_raster", type=str, help="Path to the reference raster file")
    parser.add_argument("output_raster", type=str, help="Path where the resampled raster will be saved")
    parser.add_argument("--resample", default="nearest", help="Resampling method (default: nearest). "
                        "Options: nearest, bilinear, cubic, cubicspline, lanczos, average, mode.")
    # Parse command-line arguments
    args = parser.parse_args()

    # Call function with parsed arguments
    resample_raster_using_ref_raster(args.input_raster, args.reference_raster, args.output_raster, args.resample)

