from iblatlas.atlas import ALLEN_CCF_LANDMARKS_MLAPDV_UM
import pandas as pd
import numpy as np

# print(ALLEN_CCF_LANDMARKS_MLAPDV_UM)
# output
# {'bregma': array([5739, 5400,  332])}  -- [!! CAUTION !!] this is however -- ap,lr,dv

ibl_df = pd.read_csv("ibl_channel_data.csv") # output from `downloader.py`

# (ap, dv, lr/ml) -- this  is the coordinate system needed for brainregion library points actor's coordinates
# lr and ml is the same thing, basically the side to side view

# ibl gives us the x,y,z coordinates wrt to bregma -- see this -- https://docs.internationalbrainlab.org/notebooks_external/atlas_working_with_ibllib_atlas.html#Coordinate-systems 
ibl_xyz = ibl_df[["x", "y", "z"]].to_numpy()

# we need to convert these xyz coordinates of ibl, to coordinate system used in allen atlas
# which is basically of ml(lr), ap and dv, where the origin is in the top right corner of dorsal view
# one nice thing is, ibl folks have provided us translation for bregma wrt this coordinate system -- [5739, 5400, 332]
def convert_xyz_to_ml_ap_dv(x,y,z):
    # ensure that xyz are in meters
    x = 1e6 * x
    y = 1e6 * y
    z = 1e6 * z
    if(x<0):
        ml = 5739 + abs(x)
    else:
        ml = 5739 - abs(x)
    if(y<0):
        ap = 5400 + abs(y)
    else:
        ap = 5400 - abs(y)
    if(z<0):
        dv = 332 + abs(z)
    else:
        dv = 332 - abs(z)
    return [ml,ap,dv]

ibl_ap_dv_ml = []
ibl_ml_ap_dv = []
for i in range(len(ibl_xyz)):
    ml, ap, dv = convert_xyz_to_ml_ap_dv(ibl_xyz[i][0], ibl_xyz[i][1], ibl_xyz[i][2])
    # brainrender Points expects AP, DV, ML
    ibl_ap_dv_ml.append([ap, dv, ml])
ibl_ap_dv_ml = np.array(ibl_ap_dv_ml)
for i in range(len(ibl_xyz)):
    t = convert_xyz_to_ml_ap_dv(ibl_xyz[i][0], ibl_xyz[i][1], ibl_xyz[i][2])
    ibl_ml_ap_dv.append(t)
ibl_ml_ap_dv = np.array(ibl_ml_ap_dv)



# rendering these coordinates using brainrender library

# brainrender works on the concept of scenes and actors
# we can load different scenes by using atlas_name param, it defaults to 25um resolution of mouse brain aligned to allen datasets 'allen_mouse_25um'
# and we can load different actors, like regions of brain, points, etc
# to see what all regions of brain are available -- you can see this documentation -- https://openalyx.internationalbrainlab.org/admin/experiments/brainregion/
# and the associated website -- https://openalyx.internationalbrainlab.org/admin/experiments/brainregion/ , username: intbrainlab, password: international
# this also helps understand heirarchy (ancestors and descendants wrt brain regions) 
from brainrender.actors import Points, Point
from brainrender import Scene, settings

# if true, shows axis
settings.SHOW_AXES = True
# WHOLE_SCREEN: If True, the window tries to maximize.
settings.WHOLE_SCREEN = False

pts = Points(data=ibl_ap_dv_ml,
       colors='red',
       radius=50,
       alpha=1)

scene = Scene(atlas_name="allen_mouse_25um", root=False)
scene.add_brain_region("root", alpha=0.4, color="white", silhouette=True) # root just means the whole brain, you can also see specific regions like TH (Thalamus) and more

bregma = Point([5739, 332, 5400], radius=100, color="blue", alpha=1) # we will also be able to see bregma now
scene.add(bregma)

scene.add(pts)

scene.render(camera="frontal") # there are different starting views we can set, there is also sagittal, top, etc. (look at the associated classes for get_camera)


