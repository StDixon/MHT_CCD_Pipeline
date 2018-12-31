#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 15:48:06 2018
@author: sdixon
"""

# import functions

import os, shutil, time
from astropy.io import fits
from ccdproc import ImageFileCollection
import ccdproc as ccd
import numpy as np
import re as re

# function definitions

def copyImageType(source_dir,dest_dir,keywords,image_type):
    ic = ImageFileCollection(source_dir, keywords)
    headers = ic.headers(save_location = dest_dir,keywords = image_type)

source_dir = 'samples'
input_dir = 'working/input'
bias_dir = 'working/calibration/bias'
dark_dir = 'working/calibration/dark'
flat_dir = 'working/calibration/flat'
master_dir = 'working/calibration/masters'
science_dir = 'working/science'
output_dir = 'working/output'

    
image_bias = 'Bias Frame'
image_dark = 'Dark Frame'
image_flat = 'Flat Field'
image_science = 'Light Frame'


bias_keys = {'IMAGETYP': image_bias}
dark_keys =  {'IMAGETYP': image_dark}
flat_keys =  {'IMAGETYP': image_flat}
science_keys =  {'IMAGETYP': image_science}

dark_exp = {'IMAGETYP': image_dark}

keywords = ("IMAGETYP", "FILTER", "OBJECT", "EXPTIME")

ic = ImageFileCollection(source_dir, keywords)

table = ic.summary

print(table)

bias_names = ic.files_filtered(**bias_keys)
dark_names = ic.files_filtered(**dark_keys)
flat_names = ic.files_filtered(**flat_keys)
science_names = ic.files_filtered(**science_keys)

print(repr(bias_names))
print(repr(dark_names))
print(repr(flat_names))
print(repr(science_names))

imagetypes = np.unique(table['IMAGETYP'].data).tolist()
print(repr(imagetypes))

filters = np.unique(table['FILTER'].data).tolist()
print(repr(filters))

objects = np.unique(table['OBJECT'].data).tolist()
print(repr(objects))

exposures = np.unique(table['EXPTIME'].data).tolist()
print(repr(exposures))

lists = {}

for key in keywords:
    print(repr(key))
    list = np.unique(table[key].data).tolist()
    print(repr(list))
    lists[key]=list
    print(repr(lists))

print(repr(lists['FILTER']))

