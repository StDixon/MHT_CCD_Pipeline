import platform
import os, shutil
from os import environ
from datetime import datetime
from pathlib import Path

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
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
        config_file = self.settings.get('last config').get()
        
        if config_file is None:
            config_file = 'config.ini'

        self.config_model = m.Configuration_Model(config_file)
        self.load_config(config_file)
        
        # callbacks
        self.callbacks = {
            'file->open':self.on_file_open,
            'file->save':self.on_file_save,
            'file->saveas':self.on_file_saveas,
            'file->quit':self.quit,
            'go->imagefile':self.show_imagefile,
            'go->ccdreduction':self.show_ccdreduction,
            'conf->directories':self.show_directoryinfo,
            'conf->general':self.show_generalinfo,
            'conf->biasdetails':self.show_biasinfo,
            'conf->darkdetails':self.show_darkinfo,
            'conf->flatdetails':self.show_flatinfo,
            'conf->sciencedetails':self.show_scienceinfo,
            'conf->masterdetails':self.show_masterinfo,
            'conf->reduceddetails':self.show_reducedinfo,
            'on_open_image_file':self.open_image_file,
            'reduction->go':self.create_collections,
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

        self.imagefileform.inputs['Source'].variable.trace('w', self.set_imagesource)
        self.populate_imagefileform()

        # CCD reduction form
        self.ccdreductionform = v.CCDReductionForm(
            self,
            self.settings,
            self.callbacks
        )
        self.ccdreductionform.grid(row=0,padx=10,sticky='NSEW')
        self.populate_ccdreductionform()

        # Directories Configuration form
        self.directoriesconfigurationform = v.DirectoriesConfigurationForm(
            self,
            m.Configuration_Model.fields['directories'],
            self.settings,
            self.callbacks
        )
        self.directoriesconfigurationform.grid(row=0,padx=10,sticky='NSEW')

         # General Configuration form
        self.generalconfigurationform = v.GeneralConfigurationForm(
            self,
            m.Configuration_Model.fields['general_details'],
            self.settings,
            self.callbacks
        )
        self.generalconfigurationform.grid(row=0,padx=10,sticky='NSEW')      

        # Bias Details Configuration form
        self.biasdetailsconfigurationform = v.BiasDetailsConfigurationForm(
            self,
            m.Configuration_Model.fields['bias_details'],
            self.settings,
            self.callbacks
        )
        self.biasdetailsconfigurationform.grid(row=0,padx=10,sticky='NSEW')

        # Dark Details Configuration form
        self.darkdetailsconfigurationform = v.DarkDetailsConfigurationForm(
            self,
            m.Configuration_Model.fields['dark_details'],
            self.settings,
            self.callbacks
        )
        self.darkdetailsconfigurationform.grid(row=0,padx=10,sticky='NSEW')

        # Flat Details Configuration form
        self.flatdetailsconfigurationform = v.FlatDetailsConfigurationForm(
            self,
            m.Configuration_Model.fields['flat_details'],
            self.settings,
            self.callbacks
        )
        self.flatdetailsconfigurationform.grid(row=0,padx=10,sticky='NSEW')  

        # Science Details Configuration form
        self.sciencedetailsconfigurationform = v.ScienceDetailsConfigurationForm(
            self,
            m.Configuration_Model.fields['science_details'],
            self.settings,
            self.callbacks
        )
        self.sciencedetailsconfigurationform.grid(row=0,padx=10,sticky='NSEW')

        # Master Details Configuration form
        self.masterdetailsconfigurationform = v.MasterDetailsConfigurationForm(
            self,
            m.Configuration_Model.fields['master_details'],
            self.settings,
            self.callbacks
        )
        self.masterdetailsconfigurationform.grid(row=0,padx=10,sticky='NSEW')

        # Reduced Details Configuration form
        self.reduceddetailsconfigurationform = v.ReducedDetailsConfigurationForm(
            self,
            m.Configuration_Model.fields['reduction_details'],
            self.settings,
            self.callbacks
        )
        self.reduceddetailsconfigurationform.grid(row=0,padx=10,sticky='NSEW')

        # Status Bar
        self.status = tk.StringVar()
        self.statusbar = ttk.Label(self, textvariable=self.status)
        self.statusbar.grid(sticky=(tk.W + tk.E), row=1, padx=10)

        self.populate_configurationforms()

    def populate_configurationforms(self):
        """Populate the Configuration Forms"""

        self.populate_directoriesconfigurationform()
        self.populate_generalconfigurationform()
        self.populate_biasdetailsconfigurationform() 
        self.populate_darkdetailsconfigurationform() 
        self.populate_flatdetailsconfigurationform()
        self.populate_sciencedetailsconfigurationform() 
        self.populate_masterdetailsconfigurationform()
        self.populate_reduceddetailsconfigurationform() 

    def on_file_open(self):
        """Handle the file->open action from the menu"""

        filename = filedialog.askopenfilename(
                title='Select the target file for opening',
                defaultextension='.ini',
                filetypes=(('configuration files','*.ini'),('all files','*.*')))

        if filename is None or filename == "":
            return

        filename = os.path.basename(filename)

        self.settings.get('last config').set(filename)

        self.config_model = m.Configuration_Model(filename)
        self.populate_configurationforms()
        self.load_config(filename)

    def on_file_save(self,filename=None):
        """Handle the file->save action from the menu"""
        
        self.config_model.config['directories'] = self.directoriesconfigurationform.save_form(self.config_model.config['directories'])
        self.config_model.config['general_details'] = self.generalconfigurationform.save_form(self.config_model.config['general_details'])
        self.config_model.config['bias_details'] = self.biasdetailsconfigurationform.save_form(self.config_model.config['bias_details'])
        self.config_model.config['dark_details'] = self.darkdetailsconfigurationform.save_form(self.config_model.config['dark_details'])
        self.config_model.config['flat_details'] = self.flatdetailsconfigurationform.save_form(self.config_model.config['flat_details'])
        self.config_model.config['science_details'] = self.sciencedetailsconfigurationform.save_form(self.config_model.config['science_details'])
        self.config_model.config['master_details'] = self.masterdetailsconfigurationform.save_form(self.config_model.config['master_details'])
        self.config_model.config['reduction_details'] = self.reduceddetailsconfigurationform.save_form(self.config_model.config['reduction_details'])

        self.config_model.save(filename)

        if filename is None:
            return

        self.settings['last config'].set(filename)
        
    def on_file_saveas(self):
        """Handle the file->saveas action from the menu"""
        
        filename = filedialog.asksaveasfilename(
                title='Select the target file for saving configuration',
                defaultextension='.ini',
                filetypes=(('configuration files','*.ini'),('all files','*.*')))

        if filename is None or filename == "":
            return

        filename = os.path.basename(filename)

        self.on_file_save(filename)

    def show_imagefile(self):
        """Handle the go->imagefile action from the menu"""
        self.populate_imagefileform()
        self.imagefileform.tkraise()

    def show_ccdreduction(self):
        """Handle the go->ccdreduction action from the menu"""

        self.populate_ccdreductionform()

        self.ccdreductionform.tkraise()

    def show_directoryinfo(self):
        """Handle the conf->directories action from the menu"""
        self.status.set("Directory Info Display")
 
        self.directoriesconfigurationform.tkraise()

    def show_generalinfo(self):
        """Handle the conf->general action from the menu"""
        self.status.set("General Info Display")
 
        self.generalconfigurationform.tkraise()

    def show_biasinfo(self):
        """Handle the conf->biasdetails action from the menu"""

        self.biasdetailsconfigurationform.tkraise()

    def show_darkinfo(self):
        """Handle the conf->darkdetails action from the menu"""

        self.darkdetailsconfigurationform.tkraise()

    def show_flatinfo(self):
        """Handle the conf->flatdetails action from the menu"""

        self.flatdetailsconfigurationform.tkraise()

    def show_scienceinfo(self):
        """Handle the conf->sciencedetails action from the menu"""

        self.sciencedetailsconfigurationform.tkraise()

    def show_masterinfo(self):
        """Handle the conf->masterdetails action from the menu"""

        self.masterdetailsconfigurationform.tkraise()

    def show_reducedinfo(self):
        """Handle the conf->reduceddetails action from the menu"""

        self.reduceddetailsconfigurationform.tkraise()

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
        image_path = self.imagefileform.inputs['Source'].get()
        default_path = os.path.join(working_path,image_path)
        files = Path(default_path).glob('*.fit')

        if files is None:
            return

        rows = []

        for file in files:
            path = str(file)
            filename = str(file.name)
            #parent = str(file.parent)
            #if parent == '.' or parent == image_path:
            #    parent = ''
            parent = ''
            row = {'Filename':filename,'Parent':parent,'Path':path}
            rows.append(row)

        self.imagefileform.populate_files(rows)

    def populate_ccdreductionform(self):
        
        pass 

    def populate_configurationform(self):
        
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

        #self.ccdreductionform.populate_files(rows)

    def populate_directoriesconfigurationform(self):

        self.directoriesconfigurationform.populate_form(self.config_model.config['directories'])

    def populate_generalconfigurationform(self):

        self.generalconfigurationform.populate_form(self.config_model.config['general_details'])

    def populate_biasdetailsconfigurationform(self):

        self.biasdetailsconfigurationform.populate_form(self.config_model.config['bias_details'])

    def populate_darkdetailsconfigurationform(self):

        self.darkdetailsconfigurationform.populate_form(self.config_model.config['dark_details'])

    def populate_flatdetailsconfigurationform(self):

        self.flatdetailsconfigurationform.populate_form(self.config_model.config['flat_details'])

    def populate_sciencedetailsconfigurationform(self):

        self.sciencedetailsconfigurationform.populate_form(self.config_model.config['science_details'])

    def populate_masterdetailsconfigurationform(self):

        self.masterdetailsconfigurationform.populate_form(self.config_model.config['master_details'])

    def populate_reduceddetailsconfigurationform(self):

        self.reduceddetailsconfigurationform.populate_form(self.config_model.config['reduction_details'])

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

    def load_config(self,filename = None):
        """Load configuration"""

        vartypes = {
            'bool':tk.BooleanVar,
            'str':tk.StringVar,
            'int':tk.IntVar,
            'float':tk.DoubleVar
        }

        self.configuration = {}

        # create dict of configuration variables from the model's settings.
        self.configuration['directories'] = {}
        for key, data in self.config_model.directories.items():
            vartype = vartypes.get(data['type'], tk.StringVar)
            self.configuration['directories'][key] = vartype(value=data['value'])

        self.configuration['reduction_details'] = {}
        for key, data in self.config_model.reduction_details.items():
            vartype = vartypes.get(data['type'], tk.StringVar)
            self.configuration['reduction_details'][key] = vartype(value=data['value'])

        self.configuration['master_details'] = {}
        for key, data in self.config_model.master_details.items():
            vartype = vartypes.get(data['type'], tk.StringVar)
            self.configuration['master_details'][key] = vartype(value=data['value'])

    def create_collections(self):
        #create all collections

        filemods = {}
        filemods['filename_mod_prefix'] = self.config_model.config['reduction_details'].as_bool('filename_stub_prefix')
        filemods['filename_mod'] = self.config_model.config['reduction_details']['filename_prefix_suffix_modifier']
        if filemods['filename_mod_prefix']:
            filemods['bias_removal_mod'] = self.config_model.config['reduction_details']['filename_bias_stub'] + filemods['filename_mod']
            filemods['dark_removal_mod'] = self.config_model.config['reduction_details']['filename_dark_stub'] + filemods['filename_mod']
            filemods['flat_removal_mod'] = self.config_model.config['reduction_details']['filename_flat_stub'] + filemods['filename_mod']
            filemods['reduced_removal_mod'] = self.config_model.config['reduction_details']['filename_reduced_stub'] + filemods['filename_mod']
        else:
            filemods['bias_removal_mod'] = filemods['filename_mod'] + self.config_model.config['reduction_details']['filename_bias_stub']
            filemods['dark_removal_mod'] = filemods['filename_mod'] + self.config_model.config['reduction_details']['filename_dark_stub']
            filemods['flat_removal_mod'] = filemods['filename_mod'] + self.config_model.config['reduction_details']['filename_flat_stub']
            filemods['reduced_removal_mod'] = filemods['filename_mod'] + self.config_model.config['reduction_details']['filename_reduced_stub']

        filemods['master_bias_name'] = self.config_model.config['master_details']['filename_bias']
        filemods['master_dark_name'] = self.config_model.config['master_details']['filename_dark']
        filemods['master_flat_name'] = self.config_model.config['master_details']['filename_flat']
        filemods['master_bias_header_value'] = self.config_model.config['master_details']['fits_header_image_value_bias']
        filemods['master_dark_header_value'] = self.config_model.config['master_details']['fits_header_image_value_dark']
        filemods['master_flat_header_value'] = self.config_model.config['master_details']['fits_header_image_value_flat']
        filemods['save_masters'] = self.config_model.config['directories'].as_bool('save_masters')
        filemods['save_working'] = self.config_model.config['directories'].as_bool('save_working')

        paths = {}
        paths['source_dir'] = self.config_model.config['directories']['source_dir']
        paths['bias_dir'] = os.path.join(
                                self.config_model.config['directories']['working_dir'],
                                self.config_model.config['directories']['bias_dir'])
        paths['dark_dir'] = os.path.join(
                                self.config_model.config['directories']['working_dir'],
                                self.config_model.config['directories']['dark_dir'])
        paths['flat_dir'] = os.path.join(
                                self.config_model.config['directories']['working_dir'],
                                self.config_model.config['directories']['flat_dir'])
        paths['master_dir'] = os.path.join(
                                self.config_model.config['directories']['working_dir'],
                                self.config_model.config['directories']['master_dir'])
        paths['science_dir'] = os.path.join(
                                self.config_model.config['directories']['working_dir'],
                                self.config_model.config['directories']['science_dir'])
        paths['output_dir'] = os.path.join(
                                self.config_model.config['directories']['working_dir'],
                                self.config_model.config['directories']['output_dir'])

        keywords = (self.config_model.config['general_details']['fits_header_image_type'],
                         self.config_model.config['general_details']['fits_header_filter'],
                         self.config_model.config['general_details']['fits_header_CCD_temp'],
                         self.config_model.config['general_details']['fits_header_exposure'],
                         "OBJECT")

        imagelist = (self.config_model.config['bias_details']['fits_header_image_value'],
                        self.config_model.config['dark_details']['fits_header_image_value'],
                        self.config_model.config['flat_details']['fits_header_image_value'],
                        self.config_model.config['science_details']['fits_header_image_value'],
                        )

        filelist = (self.config_model.config['bias_details']['filename_text'],
                        self.config_model.config['dark_details']['filename_text'],
                        self.config_model.config['flat_details']['filename_text'],
                        self.config_model.config['science_details']['filename_text'],
                        )

        usefitslist = (self.config_model.config['bias_details']['use_fits'],
                        self.config_model.config['dark_details']['use_fits'],
                        self.config_model.config['flat_details']['use_fits'],
                        self.config_model.config['science_details']['use_fits'],
                        )
        updatefitslist = (self.config_model.config['bias_details']['update_fits'],
                        self.config_model.config['dark_details']['update_fits'],
                        self.config_model.config['flat_details']['update_fits'],
                        self.config_model.config['science_details']['update_fits'],
                        self.config_model.config['master_details']['update_fits'],
                        )
        usefitsfilterlist = (self.config_model.config['flat_details']['use_fits_filter'],
                        self.config_model.config['science_details']['use_fits_filter'],
                        )
        updatefitsfilterlist = (self.config_model.config['flat_details']['update_fits_filter'],
                        self.config_model.config['science_details']['update_fits_filter'],
                        )


        flatfilterlist = (self.config_model.config['flat_details']['filename_text_filter'],
                        )
        sciencefilterlist = (self.config_model.config['science_details']['filename_text_filter'],
                        )
        directorylist = (paths['bias_dir'],
                            paths['dark_dir'],
                            paths['flat_dir'],
                            paths['science_dir'],
                            paths['master_dir'],
                            paths['output_dir'])

        if self.ccdreductionform.steps['single'].get() == 'False':

            subfolders = [f.name for f in os.scandir(paths['source_dir']) if f.is_dir() ] 

            print(repr(subfolders))
            print('Multiple Pass')

            for folder in subfolders:
                
                print(repr(folder))
                temp = os.path.join(self.config_model.config['directories']['source_dir'],folder)
                paths['source_dir'] = temp

                self.collection = m.ImageCollection_Model(keywords,paths,filemods,imagelist,filelist,usefitslist,updatefitslist,
                        usefitsfilterlist,updatefitsfilterlist,flatfilterlist,sciencefilterlist)

                self.collection.status.trace('w', self.reduction_status)

                self.reduce_collection(directorylist,filemods,paths)

        else:

            print('Single Pass')

            self.collection = m.ImageCollection_Model(keywords,paths,filemods,imagelist,filelist,usefitslist,updatefitslist,
                    usefitsfilterlist,updatefitsfilterlist,flatfilterlist,sciencefilterlist)

            self.collection.status.trace('w', self.reduction_status)

            self.reduce_collection(directorylist,filemods,paths)


        print('Reduction and File Copies Complete')

    def reduce_collection(self,directorylist,filemods,paths):
        """Reduce the collection"""

        m.ImageCollection_Model.reductionSetupDir(self.collection,self.settings,directorylist)

        if self.ccdreductionform.steps['CreateDir'].get() == 'True':
            m.ImageCollection_Model.reductionCreateDirectories(self.collection)
        if self.ccdreductionform.steps['CopyImages'].get() == 'True':
            m.ImageCollection_Model.reductionCopyImages(self.collection)

        m.ImageCollection_Model.reductionSetupCollections(self.collection)
        
        if self.ccdreductionform.steps['CopyImages'].get() == 'True':
            m.ImageCollection_Model.reductionCopyExpFilt(self.collection)

        if self.ccdreductionform.steps['CreateMasters'].get() == 'True':
            m.ImageCollection_Model.reductionCreateMasters(self.collection)
        if self.ccdreductionform.steps['BiasRemoval'].get() == 'True':
            m.ImageCollection_Model.reductionBiasRemoval(self.collection)
        if self.ccdreductionform.steps['DarkRemoval'].get() == 'True':
            m.ImageCollection_Model.reductionDarkRemoval(self.collection)
        if self.ccdreductionform.steps['PerformReduction'].get() == 'True':
            m.ImageCollection_Model.reductionReduceScience(self.collection)
        if self.ccdreductionform.steps['CopyResults'].get() == 'True':
            m.ImageCollection_Model.reductionCopyResults(self.collection,paths['source_dir'],
                    self.config_model.config['directories']['output_dir'],
                    paths['output_dir'])
        if self.ccdreductionform.steps['CopyWorking'].get() == 'True':
            m.ImageCollection_Model.reductionCopyWorking(self.collection,filemods,paths['source_dir'],
                    self.config_model.config['directories']['working_dir'],
                    self.config_model.config['directories']['master_dir'],
                    paths['master_dir'])
        if self.ccdreductionform.steps['DeleteDir'].get() == 'True':
            m.ImageCollection_Model.reductionDeleteDirs(self.collection,
                    self.config_model.config['directories']['working_dir'])

    def set_font(self,*args):
        font_size = self.settings['font size'].get()
        font_names = ('TkDefaultFont','TkMenuFont','TkTextFont','TkHeadingFont')
        for font_name in font_names:
            tk_font = nametofont(font_name)
            tk_font.config(size=font_size)

    def set_imagesource(self,*args):
        self.populate_imagefileform()   

    def reduction_status(self):  
        self.ccdreductionform.inputs['Status'].set(self.collection.status.get()) 