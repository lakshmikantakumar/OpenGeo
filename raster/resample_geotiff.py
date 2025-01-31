import os
import argparse
import rasterio
import numpy as np
from rasterio.enums import Resampling
from rasterio.warp import reproject
from rasterio.windows import Window

def resample_geotiff(input_raster, output_raster, target_gsd, resampling_method='nearest', block_size=(1024, 1024)):
    """
    Resamples a GeoTIFF raster to a new ground sample distance (GSD) using the specified resampling method.
    Handles large rasters or memory-constrained environments with block processing.
    """
    resampling_methods = {
        'nearest': Resampling.nearest,
        'bilinear': Resampling.bilinear,
        'cubic': Resampling.cubic,
        'cubic_spline': Resampling.cubic_spline,
        'lanczos': Resampling.lanczos,
        'average': Resampling.average,
        'mode': Resampling.mode
    }

    if resampling_method not in resampling_methods:
        raise ValueError(f"Invalid resampling method. Choose from {', '.join(resampling_methods.keys())}")

    with rasterio.open(input_raster) as src:
        src_meta = src.meta
        old_gsd = abs(src_meta['transform'][0])
        new_gsd = target_gsd

        if old_gsd == new_gsd:
            print("The target GSD is the same as the current one. No resampling needed.")
            return

        scale_factor = old_gsd / new_gsd
        new_width = int(src.width * scale_factor)
        new_height = int(src.height * scale_factor)

        new_transform = src_meta['transform'] * src_meta['transform'].scale(
            (src.width / new_width), (src.height / new_height)
        )
        new_meta = src_meta.copy()
        new_meta.update({
            'driver': 'GTiff',
            'count': src.count,
            'width': new_width,
            'height': new_height,
            'transform': new_transform,
            "compress": "LZW"
        })

        with rasterio.open(output_raster, 'w', **new_meta) as dst:
            for row_start in range(0, src.height, block_size[1]):
                for col_start in range(0, src.width, block_size[0]):
                    block_width = min(block_size[0], src.width - col_start)
                    block_height = min(block_size[1], src.height - row_start)

                    window = Window(col_start, row_start, block_width, block_height)
                    data = src.read(1, window=window)

                    new_window = Window(
                        int(col_start * scale_factor),
                        int(row_start * scale_factor),
                        int(block_width * scale_factor),
                        int(block_height * scale_factor)
                    )

                    resampled_data = np.empty((int(new_window.height), int(new_window.width)), dtype=data.dtype)

                    reproject(
                        source=data,
                        destination=resampled_data,
                        src_transform=src_meta['transform'],
                        src_crs=src_meta['crs'],
                        dst_transform=new_transform,
                        dst_crs=src_meta['crs'],
                        resampling=resampling_methods[resampling_method]
                    )

                    dst.write(resampled_data, 1, window=new_window)
        print(f"Resampling complete! Output saved to {output_raster}")

def parse_args():
    """
    Parse command-line arguments using argparse.
    
    Returns:
        args (Namespace): A Namespace object containing the command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Resample GeoTIFF raster to a new resolution.")
    parser.add_argument("--input_raster", type=str, help="Path to the input GeoTIFF raster.")
    parser.add_argument("--output_raster", type=str, help="Path to the output resampled GeoTIFF raster.")
    parser.add_argument("--target_gsd", type=float, help="Target ground sample distance (GSD) in raster units.")
    parser.add_argument("--resampling_method", type=str, default="nearest",
                        choices=["nearest", "bilinear", "cubic", "cubic_spline", "lanczos", "average", "mode"],
                        help="Resampling method to use (default: nearest).")
    parser.add_argument("--block_size", type=int, nargs=2, default=(1024, 1024),
                        help="Block size for processing (default: 1024x1024).")
    
    return parser.parse_args()

def main():
    # Parse command-line arguments
    args = parse_args()

    # Call the function to resample geotif
    resample_geotiff(args.input_raster, args.output_raster, args.target_gsd, resampling_method=args.resampling_method, block_size=tuple(args.block_size))
    
    

if __name__ == "__main__":
    main()
