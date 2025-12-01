#!/usr/bin/env python3
from pathlib import Path
import argparse
from tqdm import tqdm
from osgeo import gdal, ogr, osr


def delete_existing_vector(path: Path):
    """
    Safely deletes an existing vector file (shapefile or gpkg).
    """
    if not path.exists():
        return

    ext = path.suffix.lower()

    if ext == ".shp":
        # Delete .shp + .shx + .dbf + .prj + etc.
        for f in path.with_suffix("").parent.glob(path.stem + ".*"):
            try:
                f.unlink()
            except Exception as e:
                print(f"Warning: Could not remove {f}: {e}")
    else:
        # Delete GPKG using GDAL driver
        drv = ogr.GetDriverByName("GPKG")
        drv.DeleteDataSource(str(path))


def vectorize_mask(mask_raster_file, output_vector_file=None):
    """
    Converts a binary mask raster (0/1) to polygons.
    Uses pathlib.Path for all path handling.
    """
    mask_raster_file = Path(mask_raster_file)

    # ------------------------
    # Output path handling
    # ------------------------
    if output_vector_file is None:
        output_vector_file = mask_raster_file.with_name(mask_raster_file.stem + "_footprint.gpkg")
        print(f"Auto vector path: {output_vector_file}")
    else:
        output_vector_file = Path(output_vector_file)

    # If output is a folder → create file inside
    if output_vector_file.is_dir():
        output_vector_file = output_vector_file / f"{mask_raster_file.stem}_footprint.gpkg"
        print(f"Created vector inside folder: {output_vector_file}")

    # ------------------------
    # Open raster
    # ------------------------
    src = gdal.Open(str(mask_raster_file))
    if src is None:
        raise RuntimeError(f"Could not open raster: {mask_raster_file}")

    band = src.GetRasterBand(1)

    # ------------------------
    # Vector driver
    # ------------------------
    ext = output_vector_file.suffix.lower()
    if ext == ".shp":
        driver = ogr.GetDriverByName("ESRI Shapefile")
    elif ext == ".gpkg":
        driver = ogr.GetDriverByName("GPKG")
    else:
        raise ValueError("Unsupported vector format. Use .shp or .gpkg")

    # Delete any old file
    delete_existing_vector(output_vector_file)

    # ------------------------
    # Create vector dataset
    # ------------------------
    ds = driver.CreateDataSource(str(output_vector_file))

    # Projection
    srs = osr.SpatialReference()
    proj = src.GetProjection()
    if proj:
        srs.ImportFromWkt(proj)
    else:
        srs = None

    layer_name = output_vector_file.stem
    layer = ds.CreateLayer(layer_name, srs=srs, geom_type=ogr.wkbPolygon)

    # Add field
    field = ogr.FieldDefn("value", ogr.OFTInteger)
    layer.CreateField(field)

    # ------------------------
    # tqdm PROGRESS BAR
    # ------------------------
    print("Polygonizing (value = 1 only)...")
    pbar = tqdm(total=100, desc="Polygonizing", unit="%")

    def progress_callback(complete, message, _):
        pbar.n = int(complete * 100)
        pbar.refresh()
        return 1

    # ------------------------
    # Polygonize
    # ------------------------
    gdal.Polygonize(
        band,
        band,
        layer,
        0,
        [],
        callback=progress_callback
    )

    pbar.n = 100
    pbar.close()

    # Cleanup
    ds = None
    src.FlushCache()
    src = None

    return output_vector_file


# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Convert a mask raster (0/1) into polygons")
    parser.add_argument("raster", help="Path to the input binary (0/1) mask raster")
    parser.add_argument("-o", "--output", help="Output vector file (*.shp or *.gpkg)")

    args = parser.parse_args()
    vectorize_mask(args.raster, args.output)


if __name__ == "__main__":
    main()
