# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

#A list of imports we need for code later in the notebook.
#The css_styles() function must go last.
%matplotlib inline
from owslib.wfs import WebFeatureService
import json
from utilities import find_dict_keys
from shapely.geometry import shape, MultiPolygon
from shapely.geometry import box

import folium
from utilities import get_coords
from IPython.core.display import HTML

import time
import numpy as np
from numpy import ma
import netCDF4
import pandas as pd
from pandas import Series
import os

import matplotlib as mpl
from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib import ticker

from utilities import css_styles
css_styles()

# <codecell>

output_filename = '/home/will/Projects/testbed/test.csv'
input_directory='/augie/gluster/data/netCDF/pmel/cccma/'

# <codecell>

# Load latitude and longitude arrays
latitude = np.array(sample.variables['LATITUDE'])
longitude = np.array(sample.variables['LONGITUDE'])

# <codecell>

# Set up depth bins, for these data, they are in meters
depthbins = pd.DataFrame({'mindepth': [0, 75],
                          'maxdepth': [60, 200]},
                         index=['shallow','deep'],
                         columns=['mindepth', 'maxdepth', 'minz', 'maxz'])

depth = np.array(sample.variables['zsalt'])
depthindices=list()
for d in range(len(depthbins.index)):
    indicesz=np.where(np.logical_and(depth[:] <= depthbins.maxdepth[d],
                                     depth[:] >= depthbins.mindepth[d]))
    depthindices.append(indicesz[0])
    if len(depthindices[d]) > 0:
        depthbins.minz[d] = min(depthindices[d])
        depthbins.maxz[d] = max(depthindices[d])
        
depthbins['label']=['0 to 60 m', '75 to 200 m']

# <codecell>

#This is our known metadata for the outputs
metadata = pd.DataFrame({
         'orgName': [
                   #these don't have depth
                   'icephl_latlon','ben_latlon',
                   'aice_latlon',
                   #these do
                 'phs_latlon','phl_latlon','mzl_latlon','cop_latlon','ncao_latlon','ncas_latlon','eup_latlon','det_latlon',
                 'temp_latlon',
                 'u_latlon',
                 'v_latlon',],
         'name': ['Ice Phytoplankton Concentration',
                  'Benthos Concentration',
                  'Sea Ice Area Fraction',
                  'Small Phytoplankton Concentration',
                  'Large Phytoplankton Concentration',
                  'Large Microzooplankton Concentration',
                  'Small Coastal Copepod Concentration',
                  'Offshore Neocalanus Concentration',
                  'Neocalanus Concentration',
                  'Euphausiids Concentration',
                  'Detritus Concentration',
                  'Sea Water Temperature',
                  'Zonal (U) Current',
                  'Meridional (V) Current'],
         'units': ['mgC/m2','mgC/m2',
                   'Fraction',
                   'mgC/m3','mgC/m3','mgC/m3','mgC/m3','mgC/m3','mgC/m3','mgC/m3','mgC/m3',
                   'degrees C',
                   'm/s',
                   'm/s']
       })

# <codecell>

#this is a long way to a sorted list the files in the input directory (i.e., no files in subdirectories)
input_files = sorted([f for f in os.listdir(input_directory) if os.path.isfile(os.path.join(input_directory, f))])

# <codecell>

for f in input_files:
    print 'Working on: ' + f
    sample = netCDF4.Dataset(input_directory+f)

# <codecell>


