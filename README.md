# IBL-ephys-data

## Setup

To set up the environment, run the following commands:

```bash
uv venv --python 3.10
source .venv/bin/activate
uv pip install .
```

## Usage

To download the IBL data:

```bash
uv run downloader.py
```

To visualize the downloaded data:

```bash
uv run visualize.py
```

## To the important Stuff!!

IBL provides a couple of different datasets. 
The ones that we are concerned with are 
1. reproducible ephys data (this was used in LFP2Vec paper)
2. brainwide map data (this is the one we want to use)

## About the datasets (atleast the information we need)
* reproducible ephys has probe insertions in approximately the same locations. the researchers there were trying to see if they can produce reproducible quality experiments and results across multiple lab setups, which they were able to prove. the idea there was do the same sort of insertions across similar animal with the other setup also tried to be kept the same.
COMMENTS -- this is not really helpful to us in terms of training our model, since there are not a lot of different regions to train on. what we want to do with this is ultimately run a zero shot test to see if our model can do good predictions.
*  brainwide map data has a lot more insertions, and lawrence has been looking into it. follow up with him if needed. this data although needs to be preprocessed and then some QCs need to be run on top of it to actually make it usable. tianxiao has suggsested following the preprocessing steps in this paper [Spike sorting pipeline for the International Brain Laboratory](https://figshare.com/articles/online_resource/Spike_sorting_pipeline_for_the_International_Brain_Laboratory/19705522?file=49783080). and using something like [this](static/tianxiao_suggestions.png) for qc. but we need to think more about the qc part. qc needs to be more robustly documented and discussed and cant just be a manual check by one person if this needs to be scaled and used to get signals from brainwide data.

IBL documentation for ephys data -- https://docs.internationalbrainlab.org/notebooks_external/2024_data_release_repro_ephys.html
paper for ephys data -- https://doi.org/10.1101/2022.05.09.491042

IBL documentation for brainwide map data -- https://docs.internationalbrainlab.org/notebooks_external/2025_data_release_brainwidemap.html
paper for brainwide map data -- https://doi.org/10.6084/m9.figshare.21400815

IBL documentation on using one (pronounced O N E) for downloading its dataset --https://docs.internationalbrainlab.org/notebooks_external/data_download.html#Explore-and-download-data-using-the-ONE-api

what we were concerned with is using the SpikeSortingLoader and its channel data which has the xyz coordinates and region and label information for probe insertions across various sessions -- https://docs.internationalbrainlab.org/_autosummary/brainbox.io.one.html#brainbox.io.one.SpikeSortingLoader

Then there is also some conversion logic between IBL and Allen Atlas (which is the one brainrender library and maybe allen dataset would be using, so we need to convert IBL coordinates to Allen Coordinates)

to verify the visualization or probe information, we can confirm it using this website --
https://viz.internationalbrainlab.org/app?spikesorting=ss_2024-05-06
look under the tabs -- 'repeated sites' and 'original' for reproducible ephys data related experiments
you can search like
eid:"eid"
or
pid:"pid"


![probe trajectory visualization](static/ephys_visualization.gif)




