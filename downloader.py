import os
import numpy as np
import pandas as pd
from one.api import ONE
from brainbox.io.one import SpikeSortingLoader

def get_ibl_channel_data(eid, pid, one=None):
    """
    Fetches IBL probe data and returns a DataFrame.
    """
    print(f"Fetching data for PID: {pid}")

    # --- 1. Fetch Data from IBL ---
    if one is None:
        one = ONE(base_url='https://openalyx.internationalbrainlab.org', password='international', silent=True)
    try:
        ssl = SpikeSortingLoader(pid=pid, one=one)
        channels = ssl.load_channels()
        # channels is an ALFBunch object
        # its basically a dictionary with the following keys
        # dict_keys(['x', 'y', 'z', 'acronym', 'atlas_id', 'axial_um', 'lateral_um', 'labels', 'rawInd'])
        # atlas ids are non lateralized -- see more here what that means -- https://docs.internationalbrainlab.org/notebooks_external/atlas_working_with_ibllib_atlas.html#Lateralisation:-left/right-hemisphere-differentiation
        # basically IBL encodes both left and right hemisphere using unique positive ids, whereas Allen IDs are unique signed integers
        # where sign represents left (-ve Allen IDs) or right (+ve Allen IDs) hemisphere
        # so the number of ids in IBL are 2x Number of Allen IDs + 1 (for void region, the region outside brain)
        # The loader provides coordinates as separate x, y, z arrays in meters.
        x = channels['x']
        y = channels['y']
        z = channels['z']
        regions = channels['acronym']
        atlas_ids = channels['atlas_id']
        raw_indices = channels['rawInd']
        axial_um = channels['axial_um']
        lateral_um = channels['lateral_um']
        labels = channels['labels']
    except Exception as e:
        print(f"Could not load data for Probe {pid}. Error: {e}")
        return

    print(f"Found {len(x)} channels in {len(np.unique(regions))} unique regions.")

    # --- 3. Create a Pandas DataFrame ---
    data_to_save = {
        'session_id': eid,
        'probe_id': pid,
        'x': x,
        'y': y,
        'z': z,
        'region_acronym': regions,
        'atlas_id': atlas_ids,
        'raw_id': raw_indices,
        'axial_um': axial_um,
        'lateral_um': lateral_um,
        'label': labels
    }
    df = pd.DataFrame(data_to_save)

    return df


if __name__ == "__main__":
    import argparse
    # --- Configuration ---
    parser = argparse.ArgumentParser(description="Download IBL channel data with flexible input/output.")
    parser.add_argument("--input_csv", type=str, default=os.path.join("data", "re_eids.csv"), help="Input CSV file with eids and pids.")
    parser.add_argument("--dataset", type=str, default=None, help="Dataset name (brainwide_map, reproducible_ephys). Optional.")
    args = parser.parse_args()

    # Load EIDs and PIDs from CSV
    try:
        identifiers = pd.read_csv(args.input_csv)
    except FileNotFoundError:
        print(f"Error: {args.input_csv} not found.")
        exit(1)

    # Initialize ONE instance once
    one = ONE(base_url='https://openalyx.internationalbrainlab.org', password='international', silent=True)

    all_data = []
    # we just need pid actually
    for index, row in identifiers.iterrows():
        # Handle missing 'eid' column gracefully
        eid = row['eid'] if 'eid' in row else None
        pid = row['pid']
        df = get_ibl_channel_data(eid, pid, one=one)
        if df is not None:
            all_data.append(df)

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        # --- 3. Save the DataFrame to a CSV file ---
        # Output location logic: match visualize_allen.py for IBL datasets
        if args.dataset in ["brainwide_map", "reproducible_ephys"]:
            output_dir = os.path.join("output", "ibl", args.dataset)
            output_filename = os.path.join(output_dir, "channels.csv")
        else:
            output_dir = "output"
            output_filename = os.path.join(output_dir, "ibl_channel_data.csv")

        os.makedirs(output_dir, exist_ok=True)
        final_df.to_csv(output_filename, index=False)
        
        print(f"\nSuccessfully saved the aggregated data to '{output_filename}'")
        print(f"Total rows: {len(final_df)}")
        print("\nHere is a preview of the data:")
        print(final_df.head())
    else:
        print("No data fetched.")