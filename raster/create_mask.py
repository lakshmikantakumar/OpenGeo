#!/usr/bin/env python3
import time
import psutil
import argparse
import numpy as np
from pathlib import Path
from osgeo import gdal, ogr, osr
from tqdm import tqdm
from get_raster_info import get_raster_info


# ============================================================
#  MASK CREATION
# ============================================================

def create_mask(input_raster_file, output_mask=None):

    # Convert to Path
    input_raster_file = Path(input_raster_file)

    start_time = time.time()
    process = psutil.Process()  # For memory monitoring

    # GDAL still needs str() paths
    ds = gdal.Open(str(input_raster_file), gdal.GA_ReadOnly)
    if ds is None:
        raise RuntimeError(f"Could not open file: {input_raster_file}")

    raster_info = get_raster_info(str(input_raster_file))
    nodata_value = raster_info.get("NoData", None)
    data_type = raster_info['Data Type']
    bit_min_value = raster_info['Bit Min Value']
    bit_max_value = raster_info['Bit Max Value']
    print(f"NoData Value: {nodata_value}")
    print(f"Data Type: {data_type}")
    
    xsize = ds.RasterXSize
    ysize = ds.RasterYSize
    band = ds.GetRasterBand(1)
    band_count = ds.RasterCount
    print(f"Band Count: {band_count}")
    
    if nodata_value is not None:
        print(f"Case 1: Nodata found and NoData Value: {nodata_value}")
    else:
        if band_count >= 4:
            print(f"Case 2: Nodata None, Band 4 detected → using {bit_min_value}")
        else:
            print(f"Case 3: Nodata None, 3 bands → using {bit_min_value}/{bit_max_value}")

    # -------------------------------------------------------
    # OUTPUT MASK PATH
    # -------------------------------------------------------
    if output_mask is None:
        output_mask = input_raster_file.with_name(input_raster_file.stem + "_mask.tif")
    else:
        output_mask = Path(output_mask)

    # -------------------------------------------------------
    # CREATE OUTPUT RASTER
    # -------------------------------------------------------
    driver = gdal.GetDriverByName("GTiff")
    out_ds = driver.Create(
        str(output_mask),
        xsize,
        ysize,
        1,
        gdal.GDT_Byte,
        ["COMPRESS=LZW", "TILED=YES"]
    )

    out_ds.SetGeoTransform(ds.GetGeoTransform())
    out_ds.SetProjection(ds.GetProjection())
    out_band = out_ds.GetRasterBand(1)
    out_band.SetNoDataValue(0)

    # -------------------------------------------------------
    # SMART BLOCK SIZE SELECTION
    # -------------------------------------------------------
    internal_block_x, internal_block_y = band.GetBlockSize()

    DEFAULT_BLOCK = 1024

    if internal_block_y == 1 or internal_block_x == xsize:
        print("Striped image ― using fallback 1024×1024 blocks.")
        block_x = DEFAULT_BLOCK
        block_y = DEFAULT_BLOCK
    else:
        print(f"Using internal tile size: {internal_block_x} × {internal_block_y}")
        block_x = internal_block_x
        block_y = internal_block_y

    # -------------------------------------------------------
    # PROGRESS BAR
    # -------------------------------------------------------
    total_blocks = (
        ((ysize + block_y - 1) // block_y) *
        ((xsize + block_x - 1) // block_x)
    )
    pbar = tqdm(total=total_blocks, desc="Processing blocks", unit="block")

    # -------------------------------------------------------
    # BLOCK PROCESSING
    # -------------------------------------------------------
    for y in range(0, ysize, block_y):
        rows = min(block_y, ysize - y)

        for x in range(0, xsize, block_x):
            cols = min(block_x, xsize - x)

            # Read all bands for this block
            data = np.stack([
                ds.GetRasterBand(b + 1).ReadAsArray(x, y, cols, rows)
                for b in range(band_count)
            ], axis=0)

            # ---------------------------------------------------
            # MASK LOGIC
            # ---------------------------------------------------

            # Case 1 — nodata exists
            if nodata_value is not None:
                if np.issubdtype(data.dtype, np.floating):
                    nodata_mask = np.any(np.isclose(data, nodata_value), axis=0)
                else:
                    nodata_mask = np.any(data == nodata_value, axis=0)

                mask_block = (~nodata_mask).astype(np.uint8)

            else:
                # Case 2: band 4 exists (alpha band logic)
                if data.shape[0] >= 4:
                    band4 = data[3, :, :]
                    invalid = (band4 == bit_min_value)
                    mask_block = (~invalid).astype(np.uint8)

                # Case 3: 3-band fallback
                else:
                    all_invalid = np.all(
                        (data == bit_min_value) | (data == bit_max_value),
                        axis=0
                    )
                    mask_block = (~all_invalid).astype(np.uint8)

            # Write block
            out_band.WriteArray(mask_block, xoff=x, yoff=y)

            # Display RAM usage
            mem_mb = process.memory_info().rss / (1024 * 1024)
            pbar.set_postfix({"RAM (MB)": f"{mem_mb:.1f}"})

            pbar.update(1)

    pbar.close()

    # -------------------------------------------------------
    # CLEANUP
    # -------------------------------------------------------
    out_band.FlushCache()
    out_ds.FlushCache()
    ds = None
    out_ds = None

    elapsed = time.time() - start_time

    print(f"\nMask created: {output_mask}")
    print(f"Execution time: {elapsed:.2f} seconds")

    final_mem_mb = process.memory_info().rss / (1024 * 1024)
    print(f"Final RAM usage: {final_mem_mb:.1f} MB")

    return output_mask


# ============================================================
#  CLI
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="Create mask with pixel value 1, NoData 0 from the raster"
    )

    parser.add_argument("input_raster", help="Input raster path")
    parser.add_argument("--mask", required=False,
                        help="Output mask raster path (default: input_mask.tif)")

    args = parser.parse_args()

    create_mask(args.input_raster, args.mask)


if __name__ == "__main__":
    main()
