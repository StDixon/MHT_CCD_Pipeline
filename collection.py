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
from ccdproc import CCDData
from astropy import units as u

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

def createMasters(ImageCollection,Directory,Filename,ImageType,Filters=''):
    master_list = []
    if Filters == '':
        fnames = ImageCollection.files_filtered(imagetyp=ImageType)
    else:
        fnames = ImageCollection.files_filtered(imagetyp=ImageType,filter=Filters)
        
    for fname in fnames:
        path_file = os.path.join(ImageCollection.location,fname)
        ccd = CCDData.read(path_file, unit = u.adu)
        #this has to be fixed as the bias section does not include the whole section that will be trimmed
        #ccd = ccdproc.subtract_overscan(ccd, median=True,  overscan_axis=0, fits_section='[1:966,4105:4190]')
        #ccd = ccdproc.trim_image(ccd, fits_section=ccd.header['TRIMSEC'] )
        master_list.append(ccd)
    
    master = ccdproc.combine(master_list, method='median')
    #master_bias_blue.write('master_bias_blue.fits', clobber=True)

    m_file = os.path.join(Directory,Filename)

    master.write(m_file, overwrite=True)

def removeBias(Directory, BiasFilename, SourceFilename, DestFilename):
    master_file = os.path.join(Directory,BiasFilename)
    ccd = CCDData.read(master_file)
    bias_file = os.path.join(Directory,SourceFilename)
    master = CCDData.read(bias_file)
    master_br = ccdproc.subtract_bias(ccd,master)

    mbr_file = os.path.join(Directory,DestFilename)

    master_br.write(mbr_file, overwrite=True)
    