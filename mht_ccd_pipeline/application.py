import platform
import os
from os import environ
from datetime import datetime
from pathlib import Path

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.font import nametofont

from . import views as v
from . import models as m

from .mainmenu import get_main_menu_for_os
from .images import MHT_LOGO_32, MHT_LOGO_64

class Application(tk.Tk):
    """Application root window"""
    config_dirs = {
        'Linux':environ.get('$XDG_CONFIG_HOME','~/.config'),
        'freebsd7':environ.get('$XDG_CONFIG_HOME','~/.config'),
        'Darwin':'~/Library/Application Support',
        'Windows':'~/AppData/Local'
    }

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        self.title("MHT CCD Reduction")
        self.resizable(width=False,height=False)

        self.taskbar_icon = tk.PhotoImage(file=MHT_LOGO_64)
        self.call('wm','iconphoto',self._w,self.taskbar_icon)

        self.logo = tk.PhotoImage(file=MHT_LOGO_32)
        tk.Label(self,image=self.logo).grid(row=0)

        # File image model
        datestring = datetime.today().strftime("%Y-%m-%d")
        default_filename = "mht_data_record_{}.csv".format(datestring)
        self.filename = tk.StringVar(value=default_filename)
        self.imagefile_model = m.ImageFile_Model(filename=self.filename.get())

        # settings model & settings
        settings_dir = self.config_dirs.get(platform.system(), '~')
        self.settings_model = m.Settings_Model(path=settings_dir)
        self.load_settings()
        self.set_font()
        self.settings['font size'].trace('w', self.set_font)

        style = ttk.Style()
        theme = self.settings.get('theme').get()
        if theme in style.theme_names():
            style.theme_use(theme)

        # configuration model & settings
        config_file = 'config.ini'
        self.config_model = m.Configuration_Model()
        self.load_config()

        
        # callbacks
        self.callbacks = {
            'file->select':self.on_file_select,
            'file->quit':self.quit,
            'go->imagefile':self.show_imagefile,
            'go->ccdreduction':self.show_ccdreduction,
            'on_open_image_file':self.open_image_file,
        }

        # Menu
        menu_class = get_main_menu_for_os(platform.system())
        menu = menu_class(self,self.settings,self.callbacks)
        self.config(menu=menu)

        # Image file view form
        self.imagefileform = v.ShowImageFileForm(
            self,
            m.ImageFile_Model.fields,
            self.settings,
            self.callbacks
        )
        self.imagefileform.grid(row=0,padx=10,sticky='NSEW')
        self.populate_imagefileform()

        # CCD reduction form
        self.ccdreductionform = v.CCDReductionForm(
            self,
            self.settings,
            self.callbacks
        )
        self.imagefileform.grid(row=0,padx=10,sticky='NSEW')
        self.populate_imagefileform()

    def on_file_select(self):
        """Handle the file->select action from the menu"""
        pass

    def show_imagefile(self):
        """Handle the go->imagefile action from the menu"""
        self.populate_imagefileform()
        self.imagefileform.tkraise()

    def show_ccdreduction(self):
        """Handle the go->ccdreduction action from the menu"""
        self.create_collections()

        self.populate_ccdreductionform()
        self.ccdreductionform.tkraise()

    def open_image_file(self,filename=None):
        if filename is None:
            header = None
        else:
            try:
                header = self.imagefile_model.get_fileheader(filename)
            except Exception as e:
                messagebox.showerror(
                    title='Error',
                    message='Problem reading file',
                    detail=str(e)
                )
                return
        self.imagefileform.load_header(header)
        self.imagefileform.tkraise()

        #self.open_file_image(filename)

    def populate_imagefileform(self):
        
        working_path = '.'
        image_path = 'samples'
        default_path = os.path.join(working_path,image_path)
        files = Path(default_path).glob('*.fit')

        rows = []

        for file in files:
            path = str(file)
            filename = str(file.name)
            parent = str(file.parent)
            if parent == '.' or parent == image_path:
                parent = ''
            row = {'Filename':filename,'Parent':parent,'Path':path}
            rows.append(row)

        self.imagefileform.populate_files(rows)

    def populate_ccdreductionform(self):
        
        working_path = '.'
        image_path = 'samples'
        default_path = os.path.join(working_path,image_path)
        files = Path(default_path).glob('*.fits')

        rows = []

        for file in files:
            path = str(file)
            filename = str(file.name)
            parent = str(file.parent)
            if parent == '.' or parent == image_path:
                parent = ''
            row = {'Filename':filename,'Parent':parent,'Path':path}
            rows.append(row)

        self.ccdreductionform.populate_files(rows)

    def save_settings(self,*args):
        """Save the current settings to a preferences file"""

        for key, variable in self.settings.items():
            self.settings_model.set(key, variable.get())
        self.settings_model.save()
    
    def load_settings(self):
        """Load settings into the self.settings dict."""

        vartypes = {
            'bool':tk.BooleanVar,
            'str':tk.StringVar,
            'int':tk.IntVar,
            'float':tk.DoubleVar
        }

        # create dict of settings variables from the model's settings.
        self.settings = {}
        for key, data in self.settings_model.variables.items():
            vartype = vartypes.get(data['type'], tk.StringVar)
            self.settings[key] = vartype(value=data['value'])

        # put a trace on the variables so they get stored when changed.
        for var in self.settings.values():
            var.trace('w', self.save_settings)

    def load_config(self):
        """Load configuration"""

        vartypes = {
            'bool':tk.BooleanVar,
            'str':tk.StringVar,
            'int':tk.IntVar,
            'float':tk.DoubleVar
        }

        self.configuration = {}

        # create dict of configuration variables from the model's settings.
        self.configuration['Directories'] = {}
        for key, data in self.config_model.Directories.items():
            vartype = vartypes.get(data['type'], tk.StringVar)
            self.configuration['Directories'][key] = vartype(value=data['value'])

        self.configuration['FileModifiers'] = {}
        for key, data in self.config_model.FileModifiers.items():
            vartype = vartypes.get(data['type'], tk.StringVar)
            self.configuration['FileModifiers'][key] = vartype(value=data['value'])

        self.configuration['MasterNames'] = {}
        for key, data in self.config_model.MasterNames.items():
            vartype = vartypes.get(data['type'], tk.StringVar)
            self.configuration['MasterNames'][key] = vartype(value=data['value'])

        print(repr(self.configuration))
        

    def create_collections(self):
        #create all collections

        filemods = {}        
        filemods['bias_removal_suffix'] = '_br'
        filemods['dark_subtract_suffix'] = '_ds'
        filemods['master_bias_name'] = 'master_bias'
        filemods['master_dark_name'] = 'master_dark'
        filemods['master_flat_name'] = 'master_flat'

        paths = {}
        paths['source_dir'] = 'samples'
        paths['bias_dir'] = 'working/calibration/bias'
        paths['dark_dir'] = 'working/calibration/dark'
        paths['flat_dir'] = 'working/calibration/flat'
        paths['master_dir'] = 'working/calibration/masters'
        paths['science_dir'] = 'working/science'
        paths['output_dir'] = 'working/output'

        #keywords = ("IMAGETYP", "FILTER", "OBJECT", "EXPOSURE", "EXPTIME", "CCDTEMP")
        keywords = ("IMAGETYP", "FILTER", "OBJECT", "EXPTIME", "CCDTEMP")
        
        self.collection = m.ImageCollection_Model(keywords,paths,filemods)

        directorylist = (paths['bias_dir'],paths['dark_dir'],paths['flat_dir'],paths['science_dir'],paths['master_dir'],paths['output_dir'])

        m.ImageCollection.performreduction(self.collection,self.settings,directorylist)




    def set_font(self,*args):
        font_size = self.settings['font size'].get()
        font_names = ('TkDefaultFont','TkMenuFont','TkTextFont','TkHeadingFont')
        for font_name in font_names:
            tk_font = nametofont(font_name)
            tk_font.config(size=font_size)