import argparse
from osgeo import gdal

def get_band_min_max(input_path):
    """
    Compute min and max values for each band using GDAL.
    
    Parameters:
    - input_path : str
        Path to the input GeoTIFF file.

    Returns:
    - band_mins : list of float
    - band_maxs : list of float
    """

    ds = gdal.Open(input_path)
    if ds is None:
        raise RuntimeError("Could not open file: " + input_path)

    band_mins = []
    band_maxs = []

    for i in range(1, ds.RasterCount + 1):
        band = ds.GetRasterBand(i)

        # Compute statistics (min, max, mean, std) if missing  
        stats = band.GetStatistics(True, True)

        band_mins.append(stats[0])
        band_maxs.append(stats[1])

    ds = None
    return band_mins, band_maxs


def main():
    parser = argparse.ArgumentParser(
        description="Compute per-band min and max values for a GeoTIFF using GDAL."
    )
    parser.add_argument("input_path", help="Path to the input GeoTIFF file")

    args = parser.parse_args()

    band_mins, band_maxs = get_band_min_max_gdal(args.input_path)

    print("Band minimum values:", band_mins)
    print("Band maximum values:", band_maxs)


if __name__ == "__main__":
    main()
