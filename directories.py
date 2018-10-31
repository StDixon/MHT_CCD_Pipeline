#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 15:48:06 2018

@author: sdixon
"""

# import functions

import os, shutil, time
from astropy.io import fits

# function definitions

def createWorkingDirectories(directories):
    for dir in directories:
        if not os.path.exists(dir):
            os.makedirs(dir)

def copyFiles(source_dir,dest_dir):
    for file in os.listdir(source_dir):
        src_file = os.path.join(source_dir,file)
        shutil.copy(src_file,dest_dir)

def moveImageType(source_dir,image_type,dest_dir):
    for file in os.listdir(source_dir):
        src_file = os.path.join(source_dir,file)
        with fits.open(src_file) as hdul:
            hdr = hdul[0].header
            try:
                image = hdr['IMAGETYP']
                if image == image_type:
                    try:
                        shutil.move(src_file,dest_dir)
                    except shutil.Error:
                        print("file error")
                        os.remove(src_file)    
            except KeyError:
                print("No IMAGETYP in Header")

def splitFilters(source_dir):
    for file in os.listdir(source_dir):
        src_file = os.path.join(source_dir,file)
        if os.path.isfile(src_file):
            with fits.open(src_file) as hdul:
                hdr = hdul[0].header
                try:
                    filtertype = hdr['FILTER']
                    dest_dir = os.path.join(source_dir,filtertype)
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)
                    try:
                        shutil.move(src_file,dest_dir)
                    except shutil.Error:
                        print("file error")
                        os.remove(src_file)
                except KeyError:
                    print("No FILTER in Header")



source_dir = 'samples'
input_dir = 'working/input'
bias_dir = 'working/calibration/bias'
dark_dir = 'working/calibration/dark'
flat_dir = 'working/calibration/flat'
master_dir = 'working/calibration/masters'
science_dir = 'working/science'
output_dir = 'working/output'

directoryList = (input_dir,bias_dir,dark_dir,flat_dir,master_dir,science_dir,output_dir)

createWorkingDirectories(directoryList)

copyFiles(source_dir,input_dir)
    
image_bias = 'Bias Frame'
image_dark = 'Dark Frame'
image_flat = 'Flat Field'
image_science = 'Light Frame'

moveImageType(input_dir,image_bias,bias_dir)
moveImageType(input_dir,image_dark,dark_dir)
moveImageType(input_dir,image_flat,flat_dir)
moveImageType(input_dir,image_science,science_dir)

splitFilters(flat_dir)


    