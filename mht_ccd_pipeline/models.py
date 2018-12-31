import os, shutil
import json

import ccdproc
from ccdproc import CCDData
from ccdproc import ImageFileCollection
from astropy.io import fits
from astropy import units as u
import numpy as np

from .constants import FieldTypes as FT

class ImageFile_Model:
    """FITS file required file details"""

    fields = {
        "Filename":{'req':True,'type':FT.string},
        "Image Type":{'req':True,'type':FT.string},
        "Filter":{'req':True,'type':FT.string},
        "Exposure":{'req':True,'type':FT.decimal},
        "Header": {'req': False, 'type': FT.long_string},
        "Image": {'req': False, 'type': FT.long_string}
    }

    def __init__(self,filename):
        self.filename = filename

    def get_fileheader(self,filename):
        """ Read FITS header from file """
        if not os.path.exists(filename):
            return []
        ccd = CCDData.read(filename,unit=u.adu)
        self.fields['Header'] = ccd.header
        
        return self.fields['Header']

    def get_fileimage(self,filename):
        """ Read FITS image from file """
        if not os.path.exists(filename):
            return []
        ccd = CCDData.read(filename,unit=u.adu)
        self.fields['Image'] = ccd.data
        return self.fields['Image']

class SettingsModel:
    """A model for saving settings"""

    variables = {
        'font size': {'type':'int','value':9},
        'theme': {'type':'str','value':'default'}
    }

    def __init__(self,filename='mht_settings.json',path='~'):
        # determine the file path
        self.filepath = os.path.join(os.path.expanduser(path),filename)

        # load in saved values
        self.load()

    def set(self,key,value):
        """Set a variable value"""
        if (
            key in self.variables and
            type(value).__name__ == self.variables[key]['type']
        ):
            self.variables[key]['value'] = value
        else:
            raise ValueError("Bad key or wrong variable type")

    def save(self,settings=None):
        """Save the current settings to the file"""
        json_string = json.dumps(self.variables)
        with open(self.filepath, 'w', encoding='utf-8') as fh:
            fh.write(json_string)

    def load(self):
        """Load the settings from the file"""

        # if the file doesn't exist, return
        if not os.path.exists(self.filepath):
            return

        # open the file and read in the raw values
        with open(self.filepath,'r',encoding='utf-8') as fh:
            raw_values = json.loads(fh.read())

        # don't implicitly trust the raw values, but only get known keys
        for key in self.variables:
            if key in raw_values and 'value' in raw_values[key]:
                raw_value = raw_values[key]['value']
                self.variables[key]['value'] = raw_value

class ImageCollection():
    """Image collection model"""

    def __init__(self,keywords,paths,filemods):
        
        #directoryList use paths

        #check directories exist here
      
        self.paths = paths
        self.filemods = filemods
        self.keywords = keywords

        self.ic = ImageFileCollection(paths['source_dir'],keywords)
        self.table = self.ic.summary

        self.stats = {}

        for key in keywords:
            list = np.unique(self.table[key].data).tolist()
            self.stats[key]=list

        image_bias = 'Bias Frame'
        image_dark = 'Dark Frame'
        image_flat = 'Flat Field'
        image_science = 'Light Frame'

        bias_keys = {'IMAGETYP': image_bias}
        dark_keys =  {'IMAGETYP': image_dark}
        flat_keys =  {'IMAGETYP': image_flat}
        science_keys =  {'IMAGETYP': image_science}

        self.bias_names = self.ic.files_filtered(**bias_keys)
        self.dark_names = self.ic.files_filtered(**dark_keys)
        self.flat_names = self.ic.files_filtered(**flat_keys)
        self.science_names = self.ic.files_filtered(**science_keys)

        imageList = (image_bias, image_dark, image_flat, image_science)

    def createWorkingDirectories(self,directories):
        """Create Image Directories"""
        for dir in directories:
            if not os.path.exists(dir):
                os.makedirs(dir)

    def copyFiles(self,source_dir,dest_dir):
        for file in os.listdir(source_dir):
            src_file = os.path.join(source_dir,file)
            shutil.copy(src_file,dest_dir)

    def moveImageType(self,source_dir,image_type,dest_dir):
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
        
    def splitFilters(self,source_dir):
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

    def copyImageTypes(self,ImageCollection,directory_list,image_list):
        images = 0
        while images < len(image_list):
            self.copyImageType(ImageCollection,directory_list[images],image_list[images])
            images = images + 1


    def copyImageType(self,ImageCollection,dest_dir,image_type):
        for hdu in ImageCollection.hdus(save_location=dest_dir, imagetyp=image_type, overwrite=True):
            pass

    def fileNames(self,ImageCollection,keys,include_path= False):
        names = ImageCollection.files_filtered(**keys,include_path= include_path)
        return names

    def copyFilters(self,ImageCollection, source_dir, filters):
        for f in filters:
            dest_dir = os.path.join(source_dir,f)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
                for hdu in ImageCollection.hdus(save_location=dest_dir, filter=f, overwrite=True):
                    pass
    
    def copyExposures(self,ImageCollection, source_dir, exposures):
        for e in exposures:
            dir_name = 'exp_' + str(e)
            dest_dir = os.path.join(source_dir,dir_name)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
                for hdu in ImageCollection.hdus(save_location=dest_dir, exposure=e, overwrite=True):
                    pass

    def createMasters(self,ImageCollection,Directory,Filename,ImageType,Filters=''):
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

    def removeBias(self,Bias_Directory,Master_Directory,Dest_Directory, BiasFilename, SourceFilename, DestFilename):
        master_file = os.path.join(Master_Directory,SourceFilename)
        ccd = CCDData.read(master_file, unit = u.adu)
        bias_file = os.path.join(Bias_Directory,BiasFilename)
        master = CCDData.read(bias_file, unit = u.adu)
        master_br = ccdproc.subtract_bias(ccd,master)

        mbr_file = os.path.join(Dest_Directory,DestFilename)

        master_br.write(mbr_file, overwrite=True)


    def removeDark(self,Dark_Directory,Master_Directory,Dest_Directory, DarkFilename, SourceFilename, DestFilename):
        master_file = os.path.join(Master_Directory,SourceFilename)
        ccd = CCDData.read(master_file, unit = u.adu)
        dark_file = os.path.join(Dark_Directory,DarkFilename)
        master = CCDData.read(dark_file, unit = u.adu)
        master_brds = ccdproc.subtract_dark(ccd=ccd,master=master,exposure_time='EXPTIME',exposure_unit=u.second,scale=True)
        
        mbrds_file = os.path.join(Dest_Directory,DestFilename)

        master_brds.write(mbrds_file, overwrite=True)

    def reduceFlat(self,Flat_Directory, Source_Directory, Destination_Directory, FlatFilename,SourceFilename, DestFilename):
        master_file = os.path.join(Source_Directory,SourceFilename)
        ccd = CCDData.read(master_file, unit = u.adu)
        flat_file = os.path.join(Flat_Directory, FlatFilename)
        master = CCDData.read(flat_file, unit = u.adu)
        master_red = ccdproc.flat_correct(ccd=ccd, flat=master)
        
        mbrds_file = os.path.join(Destination_Directory,DestFilename)

        master_red.write(mbrds_file, overwrite=True)