from pathlib import Path
import os
import time
import psutil
import argparse
import numpy as np
from osgeo import gdal, ogr, osr
from tqdm import tqdm
from get_raster_info import get_raster_info
from create_mask import create_mask
from vectorize_mask import vectorize_mask

# ============================================================
#  FOOTPRINT CREATION
# ============================================================

def footprint(input_raster, footprint_path, keep_mask=False):
    """
    Creates a footprint polygon from an input raster by:
      1. Generating a binary mask raster.
      2. Vectorizing the mask into a polygon footprint.
      3. Optionally removing the temporary mask file.

    """

    # Convert to Path objects
    input_raster = Path(input_raster)
    footprint_path = Path(footprint_path)

    # Path handling using pathlib
    base = footprint_path.with_suffix("")       # remove extension
    output_mask = base.with_name(base.name + "_mask").with_suffix(".tif")

    # Create Mask
    mask_raster = create_mask(input_raster, output_mask)
    vectorize_mask(mask_raster, footprint_path)
    print(f"Mask vectorized: {footprint_path}")

    # Delete mask unless keep_mask is True
    if not keep_mask:
        try:
            output_mask.unlink()  # pathlib equivalent of os.remove
            print(f"Deleted mask raster: {output_mask}")
        except Exception as e:
            print(f"Could not delete mask raster: {e}")

    return footprint_path


# ============================================================
#  CLI
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="Create footprint from the raster"
    )

    parser.add_argument("input_raster", help="Input raster path")
    parser.add_argument("footprint", help="Output footprint vector")
    parser.add_argument("--keep-mask", action="store_true",
                        help="Keep the mask raster after vectorization")

    args = parser.parse_args()

    # Create footprint
    footprint(args.input_raster, args.footprint, args.keep_mask)


if __name__ == "__main__":
    main()
