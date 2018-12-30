import os
from .constants import FieldTypes as FT

class HeaderModel:
    """ FITS file required header details"""

    fields = {
        "Filename":{'req':True,'type':FT.string},
        "Image Type":{'req':True,'type':FT.string},
        "Filter":{'req':True,'type':FT.string},
        "Exposure":{'req':True,'type':FT.decimal},
        "Header": {'req': False, 'type': FT.long_string}
    }

    def __init__(self,filename):
        self.filename = filename

    def get_header(self):
        """ Read FITS header from file """

        if not os.path.exists(self.filename):
            return []

        