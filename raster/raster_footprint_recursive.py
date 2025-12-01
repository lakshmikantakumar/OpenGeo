#!/usr/bin/env python3
from pathlib import Path
import csv
from raster_footprint import footprint
import argparse


def batch_create_footprints(
    input_folder,
    output_folder,
    wildcard="*.tif",
    log_csv="footprint_log.csv",
    keep_mask=False
):
    """
    Batch process rasters to create footprints.

    Parameters:
        input_folder (str|Path): Root folder to search recursively
        output_folder (str|Path): Folder to save footprint files
        wildcard (str): Pattern to match rasters (e.g., *.tif)
        log_csv (str): Output CSV log filename
        keep_mask (bool): Keep intermediate mask rasters
    """

    input_folder = Path(input_folder)
    output_folder = Path(output_folder)
    wildcard_suffix = wildcard.replace("*", "").lower()

    # Ensure output folder exists
    output_folder.mkdir(parents=True, exist_ok=True)

    log_rows = []

    # Recursively walk through input folder
    for path in input_folder.rglob("*"):
        if path.is_file() and path.name.lower().endswith(wildcard_suffix):
            raster_path = path
            raster_name = raster_path.stem
            footprint_output = output_folder / f"{raster_name}_footprint.shp"

            print("\nProcessing raster:", raster_path)

            try:
                # Run footprint function
                footprint_result = footprint(
                    str(raster_path),
                    footprint_path=str(footprint_output),
                    keep_mask=keep_mask
                )

                print("✔ Footprint polygon created at:", footprint_result)

                log_rows.append([
                    str(raster_path), "Success", "", "", footprint_result
                ])

            except Exception as e:
                print("Failed to process raster:", raster_path)
                print("Error:", e)

                log_rows.append([
                    str(raster_path), "Failed", "", "", str(e)
                ])

    # Write CSV log
    log_csv_path = output_folder / log_csv
    with open(log_csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "RasterPath", "Status", "Case",
            "NoData/PossibleNoData", "FootPrintOutput/Error"
        ])
        writer.writerows(log_rows)

    print("\nBatch processing completed. Log saved at:", log_csv_path)


# =============================================================
# CLI
# =============================================================
def main():
    parser = argparse.ArgumentParser(
        description="Batch create footprints from raster files."
    )
    parser.add_argument("input", help="Input folder containing rasters")
    parser.add_argument("output", help="Output folder for footprints")
    parser.add_argument("--wildcard", default="*.tif", help="Pattern for rasters")
    parser.add_argument("--log", default="footprint_log.csv", help="CSV log filename")
    parser.add_argument("--keep-mask", action="store_true",
                        help="Keep intermediate mask rasters")

    args = parser.parse_args()

    batch_create_footprints(
        input_folder=args.input,
        output_folder=args.output,
        wildcard=args.wildcard,
        log_csv=args.log,
        keep_mask=args.keep_mask
    )


if __name__ == "__main__":
    main()
