import os, shutil
import json

import ccdproc
from ccdproc import CCDData
from ccdproc import ImageFileCollection
from astropy.io import fits
from astropy import units as u
import numpy as np

from configobj import ConfigObj

import configparser

from .constants import FieldTypes as FT

class ImageFile_Model:
    """FITS file required file details"""

    fields = {
        "Filename":{'req':True,'type':FT.string},
        "Image Type":{'req':True,'type':FT.string},
        "Filter":{'req':True,'type':FT.string},
        "Exposure":{'req':True,'type':FT.decimal},
        "Header": {'req': False, 'type': FT.long_string},
        "Image": {'req': False, 'type': FT.long_string},
        "Source": {'req': False, 'type': FT.string},
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

class Settings_Model:
    """A model for saving settings"""

    variables = {
        'font size': {'type':'int','value':9},
        'theme': {'type':'str','value':'default'},
        'last config': {'type':'str','value':'config.ini'}
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

class Configuration_Model:
    """A model for saving application configuration settings"""

    directories = {
        'source_dir': {'req': True,'type':FT.string,'value':'source'},
        'bias_dir': {'req': True,'type':FT.string,'value':'bias'},
        'dark_dir': {'req': True,'type':FT.string,'value':'dark'},
        'flat_dir': {'req': True,'type':FT.string,'value':'flat'},
        'master_dir': {'req': True,'type':FT.string,'value':'master'},
        'science_dir': {'req': True,'type':FT.string,'value':'science'},
        'output_dir': {'req': True,'type':FT.string,'value':'output'},
        'working_dir': {'req': True,'type':FT.string,'value':'working'},
        'save_masters': {'req': True,'type':FT.boolean,'value':'True'},
        'save_working': {'req': True,'type':FT.boolean,'value':'True'},
    }

    general_details = {
        'fits_header_image_type': {'req': True,'type':FT.string,'value': 'IMAGETYP'},
        'fits_header_filter': {'req': True,'type':FT.string,'value': 'FILTER'},
        'fits_header_CCD_Temp': {'req': True,'type':FT.string,'value': 'TEMP'},
        'fits_header_exposure': {'req': True,'type':FT.string,'value': 'EXPOSURE'},
    }

    bias_details = {
        'fits_header_image_value': {'req': True,'type':FT.string,'value': 'Bias Frame'},
        'filename_text': {'req': True,'type':FT.string,'value': 'bias'},
        'use_fits': {'req': False,'type':FT.rstring,'value':'True'},
        'update_fits': {'req': True,'type':FT.boolean,'value':'True'},
    }

    dark_details = {
        'fits_header_image_value': {'req': True,'type':FT.string,'value': 'Dark Frame'},
        'filename_text': {'req': True,'type':FT.string,'value': 'dark'},
        'use_fits': {'req': False,'type':FT.rstring,'value':'True'},
        'update_fits': {'req': True,'type':FT.boolean,'value':'True'},
    }

    flat_details = {
        'fits_header_image_value': {'req': True,'type':FT.string,'value': 'Flat Frame'},
        'filename_text': {'req': True,'type':FT.string,'value': 'flat'},
        'use_fits': {'req': False,'type':FT.rstring,'value':'True'},
        'update_fits': {'req': True,'type':FT.boolean,'value':'True'},
        'filename_text_filter': {'req': True,'type':FT.string,'value': {'Ha','B','R','G'}},
        'use_fits_filter': {'req': False,'type':FT.rstring,'value':'True'},
        'update_fits_filter': {'req': True,'type':FT.boolean,'value':'True'},
    }

    science_details = {
        'fits_header_image_value': {'req': True,'type':FT.string,'value': 'Light Frame'},
        'filename_text': {'req': True,'type':FT.string,'value': ''},
        'use_fits': {'req': False,'type':FT.rstring,'value':'True'},
        'update_fits': {'req': True,'type':FT.boolean,'value':'True'},
        'filename_text_filter': {'req': True,'type':FT.string,'value': {'Ha','B','R','G'}},
        'use_fits_filter': {'req': False,'type':FT.rstring,'value':'True'},
        'update_fits_filter': {'req': True,'type':FT.boolean,'value':'True'},
    }

    master_details = {
        'filename_bias': {'req': True,'type':FT.string,'value':'master_bias'},
        'filename_dark': {'req': True,'type':FT.string,'value':'master_dark'},
        'filename_flat': {'req': True,'type':FT.string,'value':'master_flat'},
        'fits_header_image_value_bias': {'req': True,'type':FT.string,'value': 'Master Bias'},
        'fits_header_image_value_dark': {'req': True,'type':FT.string,'value': 'Master Dark'},
        'fits_header_image_value_flat': {'req': True,'type':FT.string,'value': 'Master Flat'},
        'update_fits': {'req': True,'type':FT.boolean,'value':'True'},
    }

    reduction_details = {
        'filename_bias_stub': {'req': True,'type':FT.string,'value':'br'},
        'filename_dark_stub': {'req': True,'type':FT.string,'value':'ds'},
        'filename_flat_stub': {'req': True,'type':FT.string,'value':'fr'},
        'filename_reduced_stub': {'req': True,'type':FT.string,'value':'reduced'},
        'filename_stub_prefix': {'req': False,'type':FT.rstring,'value':'False'},
        'filename_prefix_suffix_modifier': {'req': True,'type':FT.string,'value':'_'},
    }

    fields = {'directories':directories,'general_details':general_details,'bias_details':bias_details,
    'dark_details':dark_details,'flat_details':flat_details,'science_details':science_details,
    'master_details':master_details,'reduction_details':reduction_details}

    def __init__(self,filename=None,path=None):
        #load in last saved config file values
        
        self.load(filename)

    def load(self,filename=None):
        """Load the configuration from the file"""
        
        if filename is None:
            filename = 'config.ini'

        # if the file doesn't exist, return
        if not os.path.exists(filename):
            return

        # Load the configuration file
        self.config = ConfigObj(filename)

        self.save()

    def save(self,filename=None):
        """Save the configuration to file"""
        if filename  is not None:
            self.config.filename = filename
        self.config.write()

    def saveas(self,filename):
        """Save the configuration to a new file"""
        self.save(filename)
        
class ImageCollection_Model():
    """Image collection model"""

    def __init__(self,keywords,paths,filemods,image_list,file_list,usefits_list,updatefits_list):
        
        self.paths = paths
        self.filemods = filemods
        self.keywords = keywords
        self.imagelist = image_list
        self.filelist = file_list
        self.usefitslist = usefits_list
        self.updatefitslist = updatefits_list
        
        self.ic = ImageFileCollection(self.paths['source_dir'],keywords=self.keywords)
        self.table = self.ic.summary

        self.stats = {}

        for key in keywords:
            list = np.unique(self.table[key].data).tolist()
            self.stats[key]=list

        bias_keys = {self.keywords[0]: self.imagelist[0]}
        dark_keys =  {self.keywords[0]: self.imagelist[1]}
        flat_keys =  {self.keywords[0]: self.imagelist[2]}
        science_keys =  {self.keywords[0]: self.imagelist[3]}

        self.bias_names = self.fileNames(self.ic,bias_keys)
        self.bias_names_full = self.fileNames(self.ic,bias_keys,include_path=True)
        self.dark_names = self.fileNames(self.ic,dark_keys)
        self.flat_names = self.fileNames(self.ic,flat_keys)
        self.science_names = self.fileNames(self.ic,science_keys)

    def createWorkingDirectories(self):
        """Create Image Directories"""
        for dir in self.directorylist:
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
                    image = hdr[self.imagelist[0]]
                    if image == image_type:
                        try:
                            shutil.move(src_file,dest_dir)
                        except shutil.Error:
                            print("file error")
                            os.remove(src_file)    
                except KeyError:
                    print("No %s in Header",self.imagelist[0])
        
    def splitFilters(self,source_dir):
        for file in os.listdir(source_dir):
            src_file = os.path.join(source_dir,file)
            if os.path.isfile(src_file):
                with fits.open(src_file) as hdul:
                    hdr = hdul[0].header
                    try:
                        filtertype = hdr[self.imagelist[1]]
                        dest_dir = os.path.join(source_dir,filtertype)
                        if not os.path.exists(dest_dir):
                            os.makedirs(dest_dir)
                        try:
                            shutil.move(src_file,dest_dir)
                        except shutil.Error:
                            print("file error")
                            os.remove(src_file)
                    except KeyError:
                        print("No %s in Header",self.imagelist[1])

    def copyImageTypes(self):
        imagetypecount = 0
        while imagetypecount < len(self.imagelist):
            
            if self.usefitslist[imagetypecount] == "True":
                self.copyImageType(self.ic,self.directorylist[imagetypecount],self.updatefitslist[imagetypecount],self.imagelist[imagetypecount])
            else:
                print(repr(self.filelist[imagetypecount]))
                tempic = ImageFileCollection(self.paths['source_dir'],keywords=self.keywords,glob_include='*'+self.filelist[imagetypecount]+'*')
                self.copyImageTypeFname(tempic,self.directorylist[imagetypecount],self.updatefitslist[imagetypecount],
                            self.imagelist[imagetypecount],self.filelist[imagetypecount])
            imagetypecount = imagetypecount + 1


    def copyImageType(self,ic,dest_dir,updatefits_list,image_type):
        #imagetyp need changing here to be the item from keywords[0]
        for hdu in ic.hdus(save_location=dest_dir, imagetyp=image_type, overwrite=True):
            pass

    def copyImageTypeFname(self,ic,dest_dir,updatefits_list,image_list,file_list):
        
        for hdu in ic.hdus(save_location=dest_dir, overwrite=True):
            if updatefits_list == "True":
                print(repr(self.keywords[0]))
                print(repr(image_list))
                hdu.header[self.keywords[0]] = image_list

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
        master_brds = ccdproc.subtract_dark(ccd=ccd,master=master,exposure_time=self.keywords[3],exposure_unit=u.second,scale=True)
        
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

    def performreduction(self,settings,directorylist):
        """All steps to perform CCD reduction"""

        self.settings = settings
        self.directorylist = directorylist

        print('Create Directories')
        self.createWorkingDirectories()

        print('Copy Images')
        self.copyImageTypes()

        print('Create Collections')
        bias_ic = ImageFileCollection(self.paths['bias_dir'], self.keywords)
        bias_table = bias_ic.summary

        flat_ic = ImageFileCollection(self.paths['flat_dir'], self.keywords)
        flat_table = flat_ic.summary
        print(repr(flat_table))

        # check and handle empty table ie no FITS files so collection empty

        flat_filters = np.unique(flat_table[self.keywords[1]].data).tolist()
        flat_exposures = np.unique(flat_table[self.keywords[3]].data).tolist()

        print('Flat Exposures')
        print(repr(flat_exposures))

        dark_ic = ImageFileCollection(self.paths['dark_dir'], self.keywords)
        dark_table = dark_ic.summary

        dark_exposures = np.unique(dark_table[self.keywords[3]].data).tolist()

        print('Dark Exposures')
        print(repr(dark_exposures))
        
        science_ic = ImageFileCollection(self.paths['science_dir'], self.keywords)
        science_table = science_ic.summary

        # need to handle 'None Type' in table
        science_filters = np.unique(science_table[self.keywords[1]].data).tolist()
        science_objects = np.unique(science_table[self.keywords[4]].data).tolist()
        science_exposures = np.unique(science_table[self.keywords[3]].data).tolist()

        print('Science Exposures')
        print(repr(science_exposures))
        print(repr(science_table))

        if True:
            return

        print('Copy Filters')
        self.copyFilters(flat_ic,self.paths['flat_dir'],flat_filters)
        self.copyFilters(science_ic,self.paths['science_dir'],science_filters)

        print('Copy Exposures')
        self.copyExposures(dark_ic,self.paths['dark_dir'],dark_exposures)

        print('Create Master Bias')
        self.createMasters(bias_ic,self.paths['master_dir'],self.filemods['master_bias_name'] + '.fit',self.imagelist[0],'')

        print('Create Master Darks')
        self.createMasters(dark_ic,self.paths['master_dir'],self.filemods['master_dark_name'] + '.fit',self.imagelist[1],'')

        print('Create Master Flats')
        for filterType in flat_filters:
            print('Create Master Flat ' + filterType)
            masterFile = self.filemods['master_flat_name'] + '_' + filterType + '.fit'
            self.createMasters(flat_ic,self.paths['master_dir'],masterFile,self.imagelist[2],filterType)

        print('Bias Removal')
        print('Bias Removal from Dark')
        if self.filemods['filename_mod_prefix']:
            self.removeBias(self.paths['master_dir'],self.paths['master_dir'],self.paths['master_dir'],self.filemods['master_bias_name'] + '.fit',self.filemods['master_dark_name'] + '.fit',self.filemods['bias_removal_mod'] + self.filemods['master_dark_name'] + '.fit')
        else:
            self.removeBias(self.paths['master_dir'],self.paths['master_dir'],self.paths['master_dir'],self.filemods['master_bias_name'] + '.fit',self.filemods['master_dark_name'] + '.fit',self.filemods['master_dark_name'] + self.filemods['bias_removal_mod'] +'.fit')

        print('Bias Removal from Flats')
        for filterType in flat_filters:
            print('Bias Removal from Flat ' + filterType)
            masterFile = self.filemods['master_flat_name'] + '_' + filterType + '.fit'
            if self.filemods['filename_mod_prefix']:
                masterFilebr = self.filemods['bias_removal_mod'] + self.filemods['master_flat_name'] + '_' + filterType + '.fit'
            else:
                masterFilebr = self.filemods['master_flat_name'] + '_' + filterType + self.filemods['bias_removal_mod'] + '.fit'

            self.removeBias(self.paths['master_dir'],self.paths['master_dir'],self.paths['master_dir'],self.filemods['master_bias_name'] + '.fit',masterFile,masterFilebr)

        print('Dark Removal from Flats')
        for filterType in flat_filters:
            print('Dark Removal from Flat ' + filterType)
            if self.filemods['filename_mod_prefix']:
                masterFilebr = self.filemods['bias_removal_mod'] + self.filemods['master_flat_name'] +'_' + filterType + '.fit'
                masterFilebrds = self.filemods['dark_removal_mod'] + self.filemods['bias_removal_mod'] + self.filemods['master_flat_name'] +'_' + filterType + '.fit'
                self.removeDark(self.paths['master_dir'],self.paths['master_dir'],self.paths['master_dir'],self.filemods['bias_removal_mod'] + self.filemods['master_dark_name'] + '.fit',masterFilebr,masterFilebrds)
            else:
                masterFilebr = self.filemods['master_flat_name'] +'_' + filterType + self.filemods['bias_removal_mod'] +'.fit'
                masterFilebrds = self.filemods['master_flat_name'] +'_' + filterType + self.filemods['bias_removal_mod'] + self.filemods['dark_removal_mod'] + '.fit'
                self.removeDark(self.paths['master_dir'],self.paths['master_dir'],self.paths['master_dir'],self.filemods['master_dark_name'] + self.filemods['bias_removal_mod'] +'.fit',masterFilebr,masterFilebrds)
               
        print('Reduce Science File')

        print('Remove Bias & Dark')
        for fname in science_ic.files:
            fname_noext = os.path.splitext(fname)[0]
            print(repr(fname_noext))
            if self.filemods['filename_mod_prefix']:
                self.removeBias(self.paths['master_dir'],self.paths['science_dir'],self.paths['output_dir'],self.filemods['master_bias_name'] + '.fit',fname,self.filemods['bias_removal_mod'] + fname_noext + '.fit')
                self.removeDark(self.paths['master_dir'],self.paths['output_dir'],self.paths['output_dir'],self.filemods['bias_removal_mod'] + self.filemods['master_dark_name'] + '.fit',self.filemods['bias_removal_mod'] + fname_noext + '.fit',self.filemods['dark_removal_mod'] + self.filemods['bias_removal_mod'] + fname_noext + '.fit')
            else:
                self.removeBias(self.paths['master_dir'],self.paths['science_dir'],self.paths['output_dir'],self.filemods['master_bias_name'] + '.fit',fname,fname_noext + self.filemods['bias_removal_mod'] + '.fit')
                self.removeDark(self.paths['master_dir'],self.paths['output_dir'],self.paths['output_dir'],self.filemods['master_dark_name'] + self.filemods['bias_removal_mod'] + '.fit',fname_noext + self.filemods['bias_removal_mod'] +'.fit',fname_noext + self.filemods['bias_removal_mod'] + self.filemods['dark_removal_mod'] + '.fit')

        print('Flat Correction')
        for filterType in flat_filters:
            print(repr(filterType))
            for fname in science_ic.files_filtered(filter=filterType):
                fname_noext = os.path.splitext(fname)[0]
                print(repr(fname_noext))
                if self.filemods['filename_mod_prefix']:
                    self.reduceFlat(self.paths['master_dir'],self.paths['output_dir'],self.paths['output_dir'],self.filemods['dark_removal_mod'] + self.filemods['bias_removal_mod'] + self.filemods['master_flat_name'] + '_' + filterType + '.fit',self.filemods['dark_removal_mod'] + self.filemods['bias_removal_mod'] + fname_noext + '.fit',self.filemods['reduced_removal_mod'] + fname_noext + '.fit')
                else:
                    self.reduceFlat(self.paths['master_dir'],self.paths['output_dir'],self.paths['output_dir'],self.filemods['master_flat_name'] + '_' + filterType + self.filemods['bias_removal_mod'] + self.filemods['dark_removal_mod'] + '.fit',fname_noext + self.filemods['bias_removal_mod'] + self.filemods['dark_removal_mod'] + '.fit',fname_noext + self.filemods['reduced_removal_mod'] + '.fit')

        print('Reduction Complete')