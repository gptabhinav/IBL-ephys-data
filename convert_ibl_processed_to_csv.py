import os
import numpy as np
import pandas as pd
import argparse
from iblatlas.atlas import BrainRegions

# Constants for Allen coordinate conversion
BREGMA_ALLEN = [5739, 5400, 332]  # ml, ap, dv

def main():
    parser = argparse.ArgumentParser(description="Convert IBL processed data to CSV with Allen coordinates, region acronym, and region id.")
    parser.add_argument("--input_csv", required=True, help="Input CSV file (IBL channels, as used in visualize.py)")
    parser.add_argument("--output_csv", required=True, help="Output CSV file")
    args = parser.parse_args()

    if not os.path.exists(args.input_csv):
        raise FileNotFoundError(f"Input file not found: {args.input_csv}")

    df = pd.read_csv(args.input_csv)
    # Use either 'region_acronym' or 'acronym' as available
    if 'region_acronym' in df.columns:
        region_col = 'region_acronym'
    elif 'acronym' in df.columns:
        region_col = 'acronym'
    else:
        raise ValueError("No region acronym column found in input CSV.")

    # Allen coordinate conversion (from visualize.py)
    def convert_xyz_to_ml_ap_dv(x, y, z):
        x = 1e6 * x
        y = 1e6 * y
        z = 1e6 * z
        if x < 0:
            ml = BREGMA_ALLEN[0] + abs(x)
        else:
            ml = BREGMA_ALLEN[0] - abs(x)
        if y < 0:
            ap = BREGMA_ALLEN[1] + abs(y)
        else:
            ap = BREGMA_ALLEN[1] - abs(y)
        if z < 0:
            dv = BREGMA_ALLEN[2] + abs(z)
        else:
            dv = BREGMA_ALLEN[2] - abs(z)
        return ap, dv, ml

    # Prepare BrainRegions for acronym to id mapping
    br = BrainRegions()

    coords = df[['x', 'y', 'z']].to_numpy()
    acronyms = df[region_col].to_numpy()
    atlas_ids = df['atlas_id'].to_numpy() if 'atlas_id' in df.columns else np.nan * np.ones(len(df))
    ap_list, dv_list, ml_list = [], [], []
    for i in range(len(coords)):
        ap, dv, ml = convert_xyz_to_ml_ap_dv(coords[i][0], coords[i][1], coords[i][2])
        ap_list.append(ap)
        dv_list.append(dv)
        ml_list.append(ml)

    out_df = pd.DataFrame({
        'ap': ap_list,
        'dv': dv_list,
        'ml': ml_list,
        'region_acronym': acronyms,
        'region_id': atlas_ids
    })
    out_df.to_csv(args.output_csv, index=False)
    print(f"Saved converted data to {args.output_csv}")

if __name__ == "__main__":
    main()
