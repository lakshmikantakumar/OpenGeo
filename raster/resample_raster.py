import argparse
import os
from osgeo import gdal

def resample_raster(input_raster, output_raster, x_res, y_res, output_bounds=None, resample_alg="nearest"):
    """
    Resamples a raster to the given resolution with optional output extent.

    Parameters:
        input_raster (str): Path to input raster.
        output_raster (str): Path to output resampled raster.
        x_res (float): Target pixel width.
        y_res (float): Target pixel height.
        output_bounds (list, optional): [xmin, ymin, xmax, ymax] for clipping. Defaults to input raster bounds.
        resample_alg (str): Resampling method (nearest, bilinear, cubic, cubicspline, lanczos, average, mode).
    """

    # Ensure input raster exists
    if not os.path.exists(input_raster):
        raise FileNotFoundError(f"Input raster not found: {input_raster}")

    # Open the input raster as a GDAL dataset
    src_ds = gdal.Open(input_raster, gdal.GA_ReadOnly)
    if src_ds is None:
        raise RuntimeError(f"Failed to open input raster: {input_raster}")

    # Get input raster bounds if not provided
    if output_bounds is None:
        gt = src_ds.GetGeoTransform()
        x_min = gt[0]
        y_max = gt[3]
        x_max = x_min + (src_ds.RasterXSize * gt[1])
        y_min = y_max + (src_ds.RasterYSize * gt[5])  # gt[5] is negative
        output_bounds = [x_min, y_min, x_max, y_max]

    # Mapping of resampling algorithms
    resampling_methods = {
        "nearest": gdal.GRA_NearestNeighbour,
        "bilinear": gdal.GRA_Bilinear,
        "cubic": gdal.GRA_Cubic,
        "cubicspline": gdal.GRA_CubicSpline,
        "lanczos": gdal.GRA_Lanczos,
        "average": gdal.GRA_Average,
        "mode": gdal.GRA_Mode,
    }

    if resample_alg.lower() not in resampling_methods:
        raise ValueError(f"Invalid resampling algorithm: {resample_alg}. Choose from {list(resampling_methods.keys())}")

    resample_alg = resampling_methods[resample_alg.lower()]

    print(f"Processing: {input_raster} → {output_raster}")
    print(f"Resolution: {x_res} x {y_res}")
    print(f"Output Bounds: {output_bounds}")
    print(f"Resampling Algorithm: {resample_alg}")

    # Create GDAL Warp options using GDALWarpAppOptions
    warp_options = gdal.WarpOptions(
        format="GTiff",
        outputBounds=output_bounds,
        xRes=x_res,
        yRes=y_res,
        resampleAlg=resample_alg,
        creationOptions=[
            "COMPRESS=LZW",  # Apply LZW compression
            "TILED=YES",      # Tile the raster for efficient reading
            "BIGTIFF=YES",    # Support large files
            "BLOCKXSIZE=256", # Tile size optimization
            "BLOCKYSIZE=256"
        ]
    )

    # Perform resampling using dataset, NOT file path
    result = gdal.Warp(output_raster, src_ds, options=warp_options)

    if result is None:
        raise RuntimeError("GDAL Warp failed. Please check input parameters.")

    print(f"Resampling complete: {output_raster}")

    # Close datasets
    src_ds = None
    result = None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resample a raster with optional extent and compression.")
    parser.add_argument("input_raster", help="Path to the input raster file")
    parser.add_argument("output_raster", help="Path to the output resampled raster file")
    parser.add_argument("x_res", type=float, help="Target pixel width (resolution)")
    parser.add_argument("y_res", type=float, help="Target pixel height (resolution)")
    parser.add_argument("--bounds", type=float, nargs=4, metavar=("xmin", "ymin", "xmax", "ymax"),
                        help="Optional: Output extent [xmin, ymin, xmax, ymax]")
    parser.add_argument("--resample", default="nearest", help="Resampling method (default: nearest). "
                        "Options: nearest, bilinear, cubic, cubicspline, lanczos, average, mode.")

    args = parser.parse_args()

    resample_raster(args.input_raster, args.output_raster, args.x_res, args.y_res, args.bounds, args.resample)
