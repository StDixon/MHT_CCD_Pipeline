#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 15:48:06 2018

@author: sdixon
"""

# import functions

import os, shutil, time
from astropy.io import fits

# create directory structure

source_dir = 'samples'
input_dir = 'working/input'
bias_dir = 'working/calibration/bias'
dark_dir = 'working/calibration/dark'
flat_dir = 'working/calibration/flat'
master_dir = 'working/calibration/masters'
science_dir = 'working/science'
output_dir = 'working/output'

if not os.path.exists(input_dir):
    os.makedirs(input_dir)
if not os.path.exists(bias_dir):
    os.makedirs(bias_dir)
if not os.path.exists(dark_dir):
    os.makedirs(dark_dir)
if not os.path.exists(flat_dir):
    os.makedirs(flat_dir)
if not os.path.exists(master_dir):
    os.makedirs(master_dir)
if not os.path.exists(science_dir):
    os.makedirs(science_dir)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Copy file from source directory to input_dir 

# commented out for testing need to reinstate    
#for file in os.listdir(source_dir):
#    src_file = os.path.join(source_dir,file)
#    shutil.copy(src_file,input_dir)

# Move Files to correct subdirectories
# IMAGETYP text indicates file use
# if no IMAGETYP in header leave in input_dir
    
image_bias = 'Bias Frame'
image_dark = 'Dark Frame'
image_flat = 'Flat Field'
image_science = 'Light Frame'

for file in os.listdir(input_dir):
    src_file = os.path.join(input_dir,file)
    with fits.open(src_file) as hdul:
        hdul.info()
        hdr = hdul[0].header
        try:
            image = hdr['IMAGETYP']
            #print(repr(image))
            if image == image_bias:
                try:
                    shutil.move(src_file,bias_dir)
                except shutil.Error:
                    print("file error")
                    os.remove(src_file)
            elif image == image_dark:
                try:
                    shutil.move(src_file,dark_dir)
                except shutil.Error:
                    print("file error")
                    os.remove(src_file)
            elif image == image_flat:
                try:
                    shutil.move(src_file,flat_dir)
                except shutil.Error:
                    print("file error")
                    os.remove(src_file)
            elif image == image_science:
                try:
                    shutil.move(src_file,science_dir)
                except shutil.Error:
                    print("file error")
                    os.remove(src_file)
        except KeyError:
            print("No IMAGETYP in Header")

# Split flats by filter type
# given by FILTER in header

for file in os.listdir(flat_dir):
    src_file = os.path.join(flat_dir,file)
    with fits.open(src_file) as hdul:
        hdul.info()
        hdr = hdul[0].header
        try:
            filtertype = hdr['FILTER']
            print(repr(filtertype))
            dest_dir = os.path.join(flat_dir,filtertype)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            try:
                shutil.move(src_file,dest_dir)
            except shutil.Error:
                print("file error")
                os.remove(src_file)
        except KeyError:
            print("No FILTER in Header")
    