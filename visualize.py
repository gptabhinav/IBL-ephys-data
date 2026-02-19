import os
import random
import numpy as np
import pandas as pd
from brainrender import Scene, settings
from brainrender.actors import Points, Point
import argparse
from iblatlas.atlas import BrainRegions

# from iblatlas.atlas import ALLEN_CCF_LANDMARKS_MLAPDV_UM
# print(ALLEN_CCF_LANDMARKS_MLAPDV_UM)
# output
# {'bregma': array([5739, 5400,  332])}  -- [!! CAUTION !!] this is however -- ap,lr,dv

# Constants
BREGMA_ALLEN = [5739, 5400, 332]  # ml, ap, dv
# one nice thing is, ibl folks have provided us translation for bregma wrt this coordinate system -- [5739, 5400, 332]

# Dataset color map (used for both legend and coloring)
DATASET_COLOR_MAP = {
    "brainwide_map": "red",
    "reproducible_ephys": "blue",
    "allen": "green"
}

def convert_xyz_to_ml_ap_dv(x, y, z):
    """
    Convert IBL xyz coordinates (in meters) to Allen Atlas ml, ap, dv coordinates (in um).
    """
    # ibl gives us the x,y,z coordinates wrt to bregma -- see this -- https://docs.internationalbrainlab.org/notebooks_external/atlas_working_with_ibllib_atlas.html#Coordinate-systems 
    
    # we need to convert these xyz coordinates of ibl, to coordinate system used in allen atlas
    # which is basically of ml(lr), ap and dv, where the origin is in the top right corner of dorsal view
    
    # ensure that xyz inputs are in meters
    # we first convert these into um (micrometers) to be used in allen atlas
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
        
    return [ml, ap, dv]

def get_region_colors(region_acronyms, dataset):
    """
    Generate a color map for unique datasets.
    """
    color = DATASET_COLOR_MAP.get(dataset, "yellow")
    point_colors = [color] * len(region_acronyms)
    return point_colors

def load_and_process_data(file_path):
    """
    Load data from CSV and process coordinates.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found at {file_path}. Please run downloader.py first.")
        
    ibl_df = pd.read_csv(file_path) # output from `downloader.py`
    
    # ibl gives us the x,y,z coordinates wrt to bregma
    ibl_xyz = ibl_df[["x", "y", "z"]].to_numpy()
    
    ibl_ap_dv_ml = []
    
    # (ap, dv, lr/ml) -- this  is the coordinate system needed for brainregion library points actor's coordinates
    # lr and ml is the same thing, basically the side to side view
    
    for i in range(len(ibl_xyz)):
        ml, ap, dv = convert_xyz_to_ml_ap_dv(ibl_xyz[i][0], ibl_xyz[i][1], ibl_xyz[i][2])
        # brainrender Points expects AP, DV, ML
        ibl_ap_dv_ml.append([ap, dv, ml])
        
    return np.array(ibl_ap_dv_ml), ibl_df["region_acronym"]

def load_and_process_data_allen(file_path):
    """
    Load Allen data from CSV and process coordinates.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found at {file_path}. Please run downloader.py first.")

    allen_df = pd.read_csv(file_path)
    # Filter out rows where both region columns are NaN -- cant do anything about this, this is how the data is
    mask = ~(allen_df["ecephys_structure_id"].isna() & allen_df["ecephys_structure_acronym"].isna())
    allen_df = allen_df[mask]

    ap = allen_df["anterior_posterior_ccf_coordinate"].to_numpy()
    dv = allen_df["dorsal_ventral_ccf_coordinate"].to_numpy()
    ml = allen_df["left_right_ccf_coordinate"].to_numpy()
    region_ids = allen_df["ecephys_structure_id"].to_numpy()

    # Fetch region acronyms using iblatlas
    try:
        br = BrainRegions()
        region_acronyms = br.get(region_ids)["acronym"]
    except ImportError:
        raise ImportError("iblatlas library is required to fetch region acronyms.")

    # Brainrender expects AP, DV, ML
    coordinates = np.column_stack([ap, dv, ml])
    return coordinates, region_acronyms

def visualize(data, colors):
    """
    Render the scene with brainrender.
    """
    # rendering these coordinates using brainrender library
    
    # brainrender works on the concept of scenes and actors
    # we can load different scenes by using atlas_name param, it defaults to 25um resolution of mouse brain aligned to allen datasets 'allen_mouse_25um'
    # and we can load different actors, like regions of brain, points, etc
    # to see what all regions of brain are available -- you can see this documentation -- https://openalyx.internationalbrainlab.org/admin/experiments/brainregion/
    # and the associated website -- https://openalyx.internationalbrainlab.org/admin/experiments/brainregion/ , username: intbrainlab, password: international
    # this also helps understand heirarchy (ancestors and descendants wrt brain regions) 

    # if true, shows axis
    settings.SHOW_AXES = True
    # WHOLE_SCREEN: If True, the window tries to maximize.
    settings.WHOLE_SCREEN = False

    # Create scene
    scene = Scene(atlas_name="allen_mouse_25um", root=False)
    
    # Add root brain region
    scene.add_brain_region("root", alpha=0.4, color="white", silhouette=True) # root just means the whole brain, you can also see specific regions like TH (Thalamus) and more

    # Add Bregma point
    bregma = Point([5739, 332, 5400], radius=100, color="blue", alpha=1) # we will also be able to see bregma now
    scene.add(bregma)

    # Add data points
    pts = Points(data=data, colors=colors, radius=20, alpha=1)
    scene.add(pts)

    # Render
    scene.render(camera="frontal") # there are different starting views we can set, there is also sagittal, top, etc. (look at the associated classes for get_camera)

def main():
    parser = argparse.ArgumentParser(description="Visualize Allen/IBL datasets (multiple supported)")
    parser.add_argument("--vendor", action="append", required=True, choices=["ibl", "allen"], help="Data vendor: ibl or allen. Can be specified multiple times.")
    parser.add_argument("--dataset", action="append", required=True, help="Dataset name: brainwide_map, reproducible_ephys, or allen. Can be specified multiple times.")
    args = parser.parse_args()

    if len(args.vendor) != len(args.dataset):
        print("Error: The number of --vendor and --dataset arguments must match.")
        return

    # Set up scene
    settings.SHOW_AXES = True
    settings.WHOLE_SCREEN = False
    scene = Scene(atlas_name="allen_mouse_25um", root=False)
    scene.add_brain_region("root", alpha=0.4, color="white", silhouette=True)
    bregma = Point([5739, 332, 5400], radius=100, color="blue", alpha=1)
    scene.add(bregma)

    # Print color legend
    legend_map = {}
    for vendor, dataset in zip(args.vendor, args.dataset):
        color = DATASET_COLOR_MAP.get(dataset, "gray")
        legend_map[f"{vendor}:{dataset}"] = color

    print("\nColor legend:")
    for k, v in legend_map.items():
        print(f"  {k} -> {v}")

    for vendor, dataset in zip(args.vendor, args.dataset):
        if vendor == "allen":
            if dataset != "allen":
                print(f"Skipping invalid combination: vendor=allen, dataset={dataset}")
                continue
            csv_path = os.path.join("output", "allen", "channels.csv")
            load_and_process_data_fn = load_and_process_data_allen
        elif vendor == "ibl":
            if dataset not in ["brainwide_map", "reproducible_ephys"]:
                print(f"Skipping invalid combination: vendor=ibl, dataset={dataset}")
                continue
            csv_path = os.path.join("output", "ibl", dataset, "channels.csv")
            load_and_process_data_fn = load_and_process_data
        else:
            print(f"Skipping invalid vendor: {vendor}")
            continue

        try:
            print(f"Loading and processing data for {vendor}:{dataset}...")
            coordinates, regions = load_and_process_data_fn(csv_path)
            print(f"Generating color map for {dataset}...")
            colors = get_region_colors(regions, dataset)
            print(f"Adding points for {vendor}:{dataset}...")
            pts = Points(data=coordinates, colors=colors, radius=20, alpha=0.5)
            scene.add(pts)
        except Exception as e:
            print(f"Error loading {vendor}:{dataset}: {e}")

    print("Visualizing...")
    scene.render(camera="frontal")

if __name__ == "__main__":
    main()


