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
import ccdproc
import numpy as np
import re

# function definitions

def copyImageTypes(ImageCollection,directory_list,image_list):
    images = 0
    while images < len(image_list):
        copyImageType(ImageCollection,directory_list[images],image_list[images])
        images = images + 1


def copyImageType(ImageCollection,dest_dir,image_type):
    for hdu in ImageCollection.hdus(save_location=dest_dir, imagetyp=image_type, overwrite=True):
        pass

def fileNames(ImageCollection,keys,include_path= False):
    names = ImageCollection.files_filtered(**keys,include_path= include_path)
    return names

def copyFilters(ImageCollection, source_dir, filters):
    for f in filters:
        dest_dir = os.path.join(source_dir,f)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            for hdu in ImageCollection.hdus(save_location=dest_dir, filter=f, overwrite=True):
                pass
    
def copyExposures(ImageCollection, source_dir, exposures):
    for e in exposures:
        dir_name = 'exp_' + str(e)
        dest_dir = os.path.join(source_dir,dir_name)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            for hdu in ImageCollection.hdus(save_location=dest_dir, exposure=e, overwrite=True):
                pass




    