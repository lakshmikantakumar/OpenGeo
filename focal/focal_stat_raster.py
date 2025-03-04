import numpy as np
import rasterio
import argparse
from numba import jit

@jit(nopython=True, parallel=True)
def focal_stat(arr, kernel_size, stat):
    """
    Applies a focal (moving window) operation on a raster array, ignoring NoData pixels.

    Parameters:
        arr (numpy.ndarray): Padded input raster block, NoData as NaN.
        kernel_size (int): Size of the focal window (must be odd).
        stat (str): Statistical operation to apply.

    Returns:
        numpy.ndarray: Processed raster block (excluding padding), with NoData retained.
    """
    pad_size = kernel_size // 2
    output = np.full_like(arr, np.nan, dtype=np.float32)  # Initialize output with NaN

    for i in range(pad_size, arr.shape[0] - pad_size):
        for j in range(pad_size, arr.shape[1] - pad_size):
            window = arr[i-pad_size:i+pad_size+1, j-pad_size:j+pad_size+1].flatten()
            
            # Exclude NaN values from calculations
            valid_values = window[~np.isnan(window)]

            if valid_values.size > 0:
                if stat == "mean":
                    output[i, j] = np.mean(valid_values)
                elif stat == "median":
                    output[i, j] = np.median(valid_values)
                elif stat == "min":
                    output[i, j] = np.min(valid_values)
                elif stat == "max":
                    output[i, j] = np.max(valid_values)
                elif stat == "std":
                    output[i, j] = np.std(valid_values)
                elif stat == "sum":
                    output[i, j] = np.sum(valid_values)
                elif stat == "range":
                    output[i, j] = np.max(valid_values) - np.min(valid_values)
                elif stat == "variance":
                    output[i, j] = np.var(valid_values)

    return output[pad_size:-pad_size, pad_size:-pad_size]  # Trim padding before returning


def focal_stat_raster(input_raster, output_raster, kernel_size, stat):
    """
    Reads a raster, applies focal statistics while properly ignoring NoData, and writes the output.

    Parameters:
        input_raster (str): Path to input raster file.
        output_raster (str): Path to save processed output raster.
        kernel_size (int): Focal window size (must be odd).
        stat (str): Statistical operation to apply.
    """
    with rasterio.open(input_raster) as src:
        meta = src.meta.copy()

        # Ensure NoData value is defined
        if src.nodata is None:
            raise ValueError("NoData value is not set in the input raster. Please define it.")

        input_nodata = src.nodata
        output_nodata = -9999  # Define a consistent NoData for output

        meta.update(dtype=rasterio.float32, compress="LZW", tiled=True, blockxsize=256, blockysize=256, nodata=output_nodata)

        with rasterio.open(output_raster, "w", **meta) as dst:
            pad_size = kernel_size // 2

            for _, window in src.block_windows(1):  # Iterate through blocks
                # Expand window for padding
                padded_window = rasterio.windows.Window(
                    max(0, window.col_off - pad_size),
                    max(0, window.row_off - pad_size),
                    min(window.width + 2 * pad_size, src.width - window.col_off),
                    min(window.height + 2 * pad_size, src.height - window.row_off),
                )

                # Read padded array
                arr = src.read(1, window=padded_window, boundless=True)

                # Convert input NoData values to NaN for correct processing
                arr = np.where(arr == input_nodata, np.nan, arr)

                # Apply focal statistics
                filtered_arr = focal_stat(arr, kernel_size, stat)

                # Convert NaN back to NoData (-9999) for writing
                filtered_arr = np.where(np.isnan(filtered_arr), output_nodata, filtered_arr)

                # Write only the actual block (removing padding)
                dst.write(filtered_arr.astype(np.float32), 1, window=window)

    print(f"Processing complete. Output saved to {output_raster}")


# Command-line argument parsing
def main():
    """
    Command-line interface for applying focal statistics on a raster file.
    """
    parser = argparse.ArgumentParser(description="Apply focal statistics on a raster dataset.")

    parser.add_argument("input_raster", type=str, help="Path to input raster file (GeoTIFF).")
    parser.add_argument("output_raster", type=str, help="Path to save the output raster.")
    parser.add_argument("kernel_size", type=int, help="Kernel size (must be an odd number, e.g., 3, 5, 7).")
    parser.add_argument("stat", type=str, choices=[
        "mean", "max", "min", "median", "std", "sum", "range", "variance", "majority", "minority", "unique_count"
    ], help="Statistical operation to apply.")

    args = parser.parse_args()

    # Ensure kernel size is odd
    if args.kernel_size % 2 == 0:
        raise ValueError("Kernel size must be an odd number (e.g., 3, 5, 7).")

    # Run focal statistics processing
    focal_stat_raster(args.input_raster, args.output_raster, args.kernel_size, args.stat)

if __name__ == "__main__":
    main()
