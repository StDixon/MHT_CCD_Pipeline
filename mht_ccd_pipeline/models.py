import os
import json

import ccdproc
from ccdproc import CCDData
from astropy import units as u

from .constants import FieldTypes as FT

class HeaderModel:
    """ FITS file required header details"""

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

    def get_header(self,filename):
        """ Read FITS header from file """
        if not os.path.exists(filename):
            return []
        ccd = CCDData.read(filename,unit=u.adu)
        self.fields['Header'] = ccd.header
        return self.fields['Header']

    def get_image(self,filename):
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
        