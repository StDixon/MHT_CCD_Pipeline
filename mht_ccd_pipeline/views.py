import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
from astropy.visualization import astropy_mpl_style

from astropy.utils.data import get_pkg_data_filename
from astropy.io import fits

from PIL import ImageTk as itk

from . import widgets as w

class ShowImageFileForm(tk.Frame):
    """Display FIT file data"""
    
    default_width = 100
    default_minwidth = 10
    default_anchor = tk.CENTER

    def __init__(self,parent,fields,settings,callbacks,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)

        self.column_defs = {
            '#0':{'label':'ID','width':50,'stretch':True,'anchor':tk.W,'command':lambda: self.sort(self.treeview,'#0')},
            'Filename':{'label':'Filename','width':150,'stretch':True,'anchor':tk.W,'command':lambda: self.sort(self.treeview,'Filename')}
           }

        self.settings = settings
        self.callbacks = callbacks

        # Styles
        style = ttk.Style()

        style.configure('headerinfo.TLabel',background='khaki')

        # Build the form
        # A dict to keep track of input widgets
        self.inputs = {}

        # header section
        headerinfo = tk.LabelFrame(
            self,
            text="Header Information",
            bg="khaki",
            padx=10,
            pady=10
        )

        #directory selection
        self.inputs['Source'] = w.LabelInput(
                headerinfo, "Source",
                field_spec=fields['Source'],
                input_args={'style':'headerinfo.TLabel'}
                )
        self.inputs['Source'].grid(row=0, column=0, columnspan=4)

        # file selection treeview
        self.treeview = ttk.Treeview(
            headerinfo,
            columns=list(self.column_defs.keys())[1:],
            selectmode='browse'
        )

        # scrollbar for treeview
        self.tvscrollbar = ttk.Scrollbar(
            headerinfo,
            orient=tk.VERTICAL,
            command=self.treeview.yview
        )
        self.treeview.configure(yscrollcommand=self.tvscrollbar.set)
        self.treeview.configure(show='headings')
        self.treeview.grid(row=1,column=0,sticky='NSEW',padx=10, pady=10)
        self.tvscrollbar.grid(row=1,column=1,sticky='NSW')

        # Configure treeview columns
        for name, definition in self.column_defs.items():
            label = definition.get('label','')
            anchor = definition.get('anchor',self.default_anchor)
            minwidth = definition.get('minwidth',self.default_minwidth)
            width = definition.get('width',self.default_width)
            stretch = definition.get('stretch',False)
            command = definition.get('command','')

            self.treeview.heading(name,text=label,anchor=anchor,command=command)
            self.treeview.column(name,anchor=anchor,minwidth=minwidth,
                                 width=width, stretch=stretch)

        # Bind double-clicks
        self.treeview.bind('<<TreeviewOpen>>',self.on_open_image_file)

        # header display
        self.inputs['Header'] = w.LabelInput(
            headerinfo, "Header",
            field_spec=fields['Header'],
            input_args={"width": 80, "height": 50}
        )

        # scrollbar for header
        self.headscrollbar = tk.Scrollbar(
            headerinfo,
            orient=tk.VERTICAL,
            command=self.inputs['Header'].input.yview)

        self.inputs['Header'].input.config(yscrollcommand=self.headscrollbar.set)

        self.inputs['Header'].input.config(state='disabled')
        self.inputs['Header'].grid(sticky="w", row=1, column=2, padx=10, pady=10)
        self.headscrollbar.grid(row=1,column=3,sticky='NSW')

        # Image display
        self.canvas = tk.Canvas(
            headerinfo, width=600,height=500
            #"Image",
            #field_spec=fields['Image'],
            #input_args={"width": 80, "height": 50}
        )
        #self.inputs['Image'].input.config(state='disabled')
        #self.canvas.create_rectangle(0,0,600,400,fill='blue')
        self.canvas.grid(sticky="w", row=1, column=5, padx=10, pady=10)

        headerinfo.grid(row=0,column=0,sticky="we")

    def populate_files(self,rows):
        """Clear the treeview and write the supplied data rows to it."""

        for row in self.treeview.get_children():
            self.treeview.delete(row)

        valuekeys = list(self.column_defs.keys())[1:]
        for rownum, rowdata in enumerate(rows):
            values = [rowdata[key] for key in valuekeys]
            parent = rowdata['Parent']
            iid = rowdata['Path']
            self.treeview.insert(parent,'end',iid=iid,
            text=str(rownum),values=values)

    def on_open_image_file(self,*args):

        selected_id = self.treeview.selection()[0]
        self.callbacks['on_open_image_file'](selected_id)

    def load_header(self,header,*args):

        self.inputs['Header'].input.config(state='normal')
        self.inputs['Header'].set(header)
        self.inputs['Header'].input.config(state='disabled')

    def load_image(self,image,*args):

        plt.style.use(astropy_mpl_style)
        plt.colorbar

        print(image.shape)
        print(repr(image))       
        
        pic = plt.imshow(image,cmap='gray')
        photo = tk.PhotoImage(master=self.canvas)
        print(repr(photo))
        self.canvas.photolist = []

        self.canvas.create_image(0,0,image=photo)
        self.canvas.photolist.append(photo)
        
        
        #self.inputs['Image'].input.config(state='normal')
        #self.inputs['Image'].set(hold)
        #self.inputs['Image'].input.config(state='disabled')
 
    def sort(self,treeview,col):
        itemlist = list(treeview.get_children(''))
        itemlist.sort(key=lambda x:treeview.set(x,col))
        for index, iid in enumerate(itemlist):
            treeview.move(iid,treeview.parent(iid),index)

class CCDReductionForm(tk.Frame):
    """CCD Reduction"""
    
    default_width = 100
    default_minwidth = 10
    default_anchor = tk.CENTER

    def __init__(self,parent,settings,callbacks,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)

        self.column_defs = {
            '#0':{'label':'ID','width':50,'stretch':True,'anchor':tk.W,'command':lambda: self.sort(self.treeview,'#0')},
            'Filename':{'label':'Filename','width':150,'stretch':True,'anchor':tk.W,'command':lambda: self.sort(self.treeview,'Filename')}
           }

        self.settings = settings
        self.callbacks = callbacks

        # main section
        mainframe = tk.LabelFrame(
            self,
            text="File Information",
            bg="khaki",
            padx=10,
            pady=10
        )

        # collection treeview
        self.treeview = ttk.Treeview(
            self,
            columns=list(self.column_defs.keys())[1:],
            selectmode='none'
        )

        # scrollbar for treeview
        self.scrollbar = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self.treeview.yview
        )
        self.treeview.configure(yscrollcommand=self.scrollbar.set)
        self.treeview.configure(show='headings')
        self.treeview.grid(row=0,column=0,sticky='NSEW',padx=10,pady=10)
        self.scrollbar.grid(row=0,column=1,sticky='NSW')

        # Configure treeview columns
        for name, definition in self.column_defs.items():
            label = definition.get('label','')
            anchor = definition.get('anchor',self.default_anchor)
            minwidth = definition.get('minwidth',self.default_minwidth)
            width = definition.get('width',self.default_width)
            stretch = definition.get('stretch',False)
            command = definition.get('command','')

            self.treeview.heading(name,text=label,anchor=anchor,command=command)
            self.treeview.column(name,anchor=anchor,minwidth=minwidth,
                                 width=width, stretch=stretch)

        mainframe.grid(row=0,column=0,sticky="we")

    def populate_files(self,rows):
        """Clear the treeview and write the supplied data rows to it."""

        for row in self.treeview.get_children():
            self.treeview.delete(row)

        valuekeys = list(self.column_defs.keys())[1:]
        for rownum, rowdata in enumerate(rows):
            values = [rowdata[key] for key in valuekeys]
            parent = rowdata['Parent']
            iid = rowdata['Path']
            self.treeview.insert(parent,'end',iid=iid,
            text=str(rownum),values=values)

    def sort(self,treeview,col):
        itemlist = list(treeview.get_children(''))
        itemlist.sort(key=lambda x:treeview.set(x,col))
        for index, iid in enumerate(itemlist):
            treeview.move(iid,treeview.parent(iid),index)

class ConfigurationForm(tk.Frame):
    """The configuration form"""
    
    def __init__(self, parent, fields, settings, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.settings = settings
        self.callbacks = callbacks
        
        self.current_record = None
        # A dict to keep track of input widgets
        self.inputs = {}
        
        # Styles
        style = ttk.Style()
        
        style.configure('Directories.TLabel',background='khaki')
        style.configure('Directories.TCheckbutton',background='khaki')
        style.configure('GeneralDetails.TLabel',background='lightblue')
        style.configure('GeneralDetails.TCheckbutton',background='lightblue')
        style.configure('BiasDetails.TLabel',background='lightgreen')
        style.configure('BiasDetails.TCheckbutton',background='lightgreen')
        style.configure('DarkDetails.TLabel',background='lightgreen')
        style.configure('DarkDetails.TCheckbutton',background='lightgreen')
        style.configure('FlatDetails.TLabel',background='lightgreen')
        style.configure('FlatDetails.TCheckbutton',background='lightgreen')
        style.configure('ScienceDetails.TLabel',background='lightgreen')
        style.configure('ScienceDetails.TCheckbutton',background='lightgreen')
        style.configure('MasterDetails.TLabel',background='lightgreen')
        style.configure('MasterDetails.TCheckbutton',background='lightgreen')
        style.configure('ReductionDetails.TLabel',background='lightgreen')
        style.configure('ReductionDetails.TCheckbutton',background='lightgreen')
        
        # Directories
        Directories = tk.LabelFrame(self, 
                                   text="Directories",
                                   bg="Khaki",
                                   padx=10,
                                   pady=10
                                   )
        
        # Line 1
        self.inputs['Source'] = w.LabelInput(
                Directories, "Source",
                field_spec=fields['directories']['source_dir'],
                label_args={'style':'Directories.TLabel'})
        self.inputs['Source'].grid(row=0, column=0)

        self.inputs['Science'] = w.LabelInput(
                Directories, "Science",
                field_spec=fields['directories']['science_dir'],
                label_args={'style':'Directories.TLabel'})
        self.inputs['Science'].grid(row=0, column=1)

        self.inputs['Masters'] = w.LabelInput(
                Directories, "Masters",
                field_spec=fields['directories']['master_dir'],
                label_args={'style':'Directories.TLabel'})
        self.inputs['Masters'].grid(row=0, column=2)
       
        # Line 2
        self.inputs['Bias'] = w.LabelInput(
                Directories, "Bias",
                field_spec=fields['directories']['bias_dir'],
                label_args={'style':'Directories.TLabel'})
        self.inputs['Bias'].grid(row=1, column=0)

        self.inputs['Dark'] = w.LabelInput(
                Directories, "Dark",
                field_spec=fields['directories']['dark_dir'],
                label_args={'style':'Directories.TLabel'})
        self.inputs['Dark'].grid(row=1, column=1)

        self.inputs['Flat'] = w.LabelInput(
                Directories, "Flat",
                field_spec=fields['directories']['flat_dir'],
                label_args={'style':'Directories.TLabel'})
        self.inputs['Flat'].grid(row=1, column=2)

        # Line 3
        self.inputs['Working'] = w.LabelInput(
                Directories, "Working",
                field_spec=fields['directories']['working_dir'],
                label_args={'style':'Directories.TLabel'})
        self.inputs['Working'].grid(row=2, column=0)

        self.inputs['Output'] = w.LabelInput(
                Directories, "Output",
                field_spec=fields['directories']['output_dir'],
                label_args={'style':'Directories.TLabel'})
        self.inputs['Output'].grid(row=2, column=1)

        #Line 4
        self.inputs['Save Masters'] = w.LabelInput(
                Directories, "Save Masters",
                field_spec=fields['directories']['save_masters'],
                label_args={'style':'Directories.TLabel'},
                input_args={'style':'Directories.TCheckbutton'})
        self.inputs['Save Masters'].grid(row=3, column=0, columnspan=3)

        #Line 5
        self.inputs['Save Working'] = w.LabelInput(
                Directories, "Save Working",
                field_spec=fields['directories']['save_working'],
                label_args={'style':'Directories.TLabel'},
                input_args={'style':'Directories.TCheckbutton'})
        self.inputs['Save Working'].grid(row=4, column=0, columnspan=3)
        
        Directories.grid(row=0, column=0, sticky=tk.W + tk.E)

        # General Details
        GeneralDetails = tk.LabelFrame(self, 
                                   text="General Details",
                                   bg="lightblue",
                                   padx=10,
                                   pady=10
                                   )
        
        # Line 1
        self.inputs['FITS Header Exposure'] = w.LabelInput(
                GeneralDetails, "FITS Header Exposure",
                field_spec=fields['general_details']['fits_header_exposure'],
                label_args={'style':'GeneralDetails.TLabel'})
        self.inputs['FITS Header Exposure'].grid(row=0, column=0)

        self.inputs['FITS Header CCD Temp'] = w.LabelInput(
                GeneralDetails, "FITS Header CCD Temp",
                field_spec=fields['general_details']['fits_header_CCD_Temp'],
                label_args={'style':'GeneralDetails.TLabel'})
        self.inputs['FITS Header CCD Temp'].grid(row=0, column=1)

        GeneralDetails.grid(row=0, column=1, sticky=tk.W + tk.E)

        # Bias Details
        BiasDetails = tk.LabelFrame(self, 
                                   text="Bias Details",
                                   bg="lightgreen",
                                   padx=10,
                                   pady=10
                                   )
        
        # Line 1
        self.inputs['FITS Header Image'] = w.LabelInput(
                BiasDetails, "FITS Header Image",
                field_spec=fields['bias_details']['fits_header_image'],
                label_args={'style':'BiasDetails.TLabel'})
        self.inputs['FITS Header Image'].grid(row=0, column=0)

        self.inputs['FITS Header Value'] = w.LabelInput(
                BiasDetails, "FITS Header Value",
                field_spec=fields['bias_details']['fits_header_image_value'],
                label_args={'style':'BiasDetails.TLabel'})
        self.inputs['FITS Header Value'].grid(row=0, column=1)

        self.inputs['Filename Text'] = w.LabelInput(
                BiasDetails, "Filename Text",
                field_spec=fields['bias_details']['filename_text'],
                label_args={'style':'BiasDetails.TLabel'})
        self.inputs['Filename Text'].grid(row=0, column=2)

        #Line 2
        self.inputs['Use FITS Header'] = w.LabelInput(
                BiasDetails, "Use FITS Header",
                field_spec=fields['bias_details']['use_fits'],
                label_args={'style':'BiasDetails.TLabel'},
                input_args={'style':'BiasDetails.TCheckbutton'})
        self.inputs['Use FITS Header'].grid(row=1, column=0, columnspan=1)

        self.inputs['Use Filename'] = w.LabelInput(
                BiasDetails, "Use Filename",
                field_spec=fields['bias_details']['use_filename'],
                label_args={'style':'BiasDetails.TLabel'},
                input_args={'style':'BiasDetails.TCheckbutton'})
        self.inputs['Use Filename'].grid(row=1, column=1, columnspan=1)

        #Line 3
        self.inputs['Update FITS Header'] = w.LabelInput(
                BiasDetails, "Update FITS Header",
                field_spec=fields['bias_details']['update_fits'],
                label_args={'style':'BiasDetails.TLabel'},
                input_args={'style':'BiasDetails.TCheckbutton'})
        self.inputs['Update FITS Header'].grid(row=2, column=0, columnspan=3)

        BiasDetails.grid(row=1, column=0, sticky=tk.W + tk.E)

        # Dark Details
        DarkDetails = tk.LabelFrame(self, 
                                   text="Dark Details",
                                   bg="lightgreen",
                                   padx=10,
                                   pady=10
                                   )
        
        # Line 1
        self.inputs['FITS Header Image'] = w.LabelInput(
                DarkDetails, "FITS Header Image",
                field_spec=fields['dark_details']['fits_header_image'],
                label_args={'style':'DarkDetails.TLabel'})
        self.inputs['FITS Header Image'].grid(row=0, column=0)

        self.inputs['FITS Header Value'] = w.LabelInput(
                DarkDetails, "FITS Header Value",
                field_spec=fields['dark_details']['fits_header_image_value'],
                label_args={'style':'DarkDetails.TLabel'})
        self.inputs['FITS Header Value'].grid(row=0, column=1)

        self.inputs['Filename Text'] = w.LabelInput(
                DarkDetails, "Filename Text",
                field_spec=fields['dark_details']['filename_text'],
                label_args={'style':'DarkDetails.TLabel'})
        self.inputs['Filename Text'].grid(row=0, column=2)

        #Line 2
        self.inputs['Use FITS Header'] = w.LabelInput(
                DarkDetails, "Use FITS Header",
                field_spec=fields['dark_details']['use_fits'],
                label_args={'style':'DarkDetails.TLabel'},
                input_args={'style':'DarkDetails.TCheckbutton'})
        self.inputs['Use FITS Header'].grid(row=1, column=0, columnspan=3)

        #Line 3
        self.inputs['Use Filename'] = w.LabelInput(
                DarkDetails, "Use Filename",
                field_spec=fields['dark_details']['use_filename'],
                label_args={'style':'DarkDetails.TLabel'},
                input_args={'style':'DarkDetails.TCheckbutton'})
        self.inputs['Use Filename'].grid(row=2, column=0, columnspan=1)

        self.inputs['Update FITS Header'] = w.LabelInput(
                DarkDetails, "Update FITS Header",
                field_spec=fields['dark_details']['update_fits'],
                label_args={'style':'DarkDetails.TLabel'},
                input_args={'style':'DarkDetails.TCheckbutton'})
        self.inputs['Update FITS Header'].grid(row=2, column=1, columnspan=1)

        DarkDetails.grid(row=1, column=1, sticky=tk.W + tk.E)

        # Flat Details
        FlatDetails = tk.LabelFrame(self, 
                                   text="Flat Details",
                                   bg="lightgreen",
                                   padx=10,
                                   pady=10
                                   )
        
        # Line 1
        self.inputs['FITS Header Image'] = w.LabelInput(
                FlatDetails, "FITS Header Image",
                field_spec=fields['flat_details']['fits_header_image'],
                label_args={'style':'FlatDetails.TLabel'})
        self.inputs['FITS Header Image'].grid(row=0, column=0)

        self.inputs['FITS Header Value'] = w.LabelInput(
                FlatDetails, "FITS Header Value",
                field_spec=fields['flat_details']['fits_header_image_value'],
                label_args={'style':'FlatDetails.TLabel'})
        self.inputs['FITS Header Value'].grid(row=0, column=1)

        self.inputs['Filename Text'] = w.LabelInput(
                FlatDetails, "Filename Text",
                field_spec=fields['flat_details']['filename_text'],
                label_args={'style':'FlatDetails.TLabel'})
        self.inputs['Filename Text'].grid(row=0, column=2)

        #Line 2
        self.inputs['Use FITS Header'] = w.LabelInput(
                FlatDetails, "Use FITS Header",
                field_spec=fields['flat_details']['use_fits'],
                label_args={'style':'FlatDetails.TLabel'},
                input_args={'style':'FlatDetails.TCheckbutton'})
        self.inputs['Use FITS Header'].grid(row=1, column=0, columnspan=1)

        self.inputs['Use Filename'] = w.LabelInput(
                FlatDetails, "Use Filename",
                field_spec=fields['flat_details']['use_filename'],
                label_args={'style':'FlatDetails.TLabel'},
                input_args={'style':'FlatDetails.TCheckbutton'})
        self.inputs['Use Filename'].grid(row=1, column=1, columnspan=1)

        #Line 3
        self.inputs['Update FITS Header'] = w.LabelInput(
                FlatDetails, "Update FITS Header",
                field_spec=fields['flat_details']['update_fits'],
                label_args={'style':'FlatDetails.TLabel'},
                input_args={'style':'FlatDetails.TCheckbutton'})
        self.inputs['Update FITS Header'].grid(row=2, column=0, columnspan=3)

        # Line 4
        self.inputs['FITS Header Filter'] = w.LabelInput(
                FlatDetails, "FITS Header Filter",
                field_spec=fields['flat_details']['fits_header_filter'],
                label_args={'style':'FlatDetails.TLabel'})
        self.inputs['FITS Header Filter'].grid(row=3, column=0)

        self.inputs['Filename Filter Text'] = w.LabelInput(
                FlatDetails, "Filename Filter Text",
                field_spec=fields['flat_details']['filename_text_filter'],
                label_args={'style':'FlatDetails.TLabel'})
        self.inputs['Filename Filter Text'].grid(row=3, column=1)

        #Line 5
        self.inputs['Use FITS Filter'] = w.LabelInput(
                FlatDetails, "Use FITS Filter",
                field_spec=fields['flat_details']['use_fits_filter'],
                label_args={'style':'FlatDetails.TLabel'},
                input_args={'style':'FlatDetails.TCheckbutton'})
        self.inputs['Use FITS Filter'].grid(row=4, column=0, columnspan=1)

        self.inputs['Use Filename Filter'] = w.LabelInput(
                FlatDetails, "Use Filename Filter",
                field_spec=fields['flat_details']['use_filename_filter'],
                label_args={'style':'FlatDetails.TLabel'},
                input_args={'style':'FlatDetails.TCheckbutton'})
        self.inputs['Use Filename Filter'].grid(row=4, column=1, columnspan=1)

        #Line 6
        self.inputs['Update FITS Header Filter'] = w.LabelInput(
                FlatDetails, "Update FITS Header Filter",
                field_spec=fields['flat_details']['update_fits_filter'],
                label_args={'style':'FlatDetails.TLabel'},
                input_args={'style':'FlatDetails.TCheckbutton'})
        self.inputs['Update FITS Header Filter'].grid(row=5, column=0, columnspan=3)

        FlatDetails.grid(row=2, column=0, sticky=tk.W + tk.E)

        # Science Details
        ScienceDetails = tk.LabelFrame(self, 
                                   text="Science Details",
                                   bg="lightgreen",
                                   padx=10,
                                   pady=10
                                   )
        
        # Line 1
        self.inputs['FITS Header Image'] = w.LabelInput(
                ScienceDetails, "FITS Header Image",
                field_spec=fields['science_details']['fits_header_image'],
                label_args={'style':'ScienceDetails.TLabel'})
        self.inputs['FITS Header Image'].grid(row=0, column=0)

        self.inputs['FITS Header Value'] = w.LabelInput(
                ScienceDetails, "FITS Header Value",
                field_spec=fields['science_details']['fits_header_image_value'],
                label_args={'style':'ScienceDetails.TLabel'})
        self.inputs['FITS Header Value'].grid(row=0, column=1)

        self.inputs['Filename Text'] = w.LabelInput(
                ScienceDetails, "Filename Text",
                field_spec=fields['science_details']['filename_text'],
                label_args={'style':'ScienceDetails.TLabel'})
        self.inputs['Filename Text'].grid(row=0, column=2)

        #Line 2
        self.inputs['Use FITS Header'] = w.LabelInput(
                ScienceDetails, "Use FITS Header",
                field_spec=fields['science_details']['use_fits'],
                label_args={'style':'ScienceDetails.TLabel'},
                input_args={'style':'ScienceDetails.TCheckbutton'})
        self.inputs['Use FITS Header'].grid(row=1, column=0, columnspan=1)

        self.inputs['Use Filename'] = w.LabelInput(
                ScienceDetails, "Use Filename",
                field_spec=fields['science_details']['use_filename'],
                label_args={'style':'ScienceDetails.TLabel'},
                input_args={'style':'ScienceDetails.TCheckbutton'})
        self.inputs['Use Filename'].grid(row=1, column=1, columnspan=1)

        #Line 3
        self.inputs['Update FITS Header'] = w.LabelInput(
                ScienceDetails, "Update FITS Header",
                field_spec=fields['science_details']['update_fits'],
                label_args={'style':'ScienceDetails.TLabel'},
                input_args={'style':'ScienceDetails.TCheckbutton'})
        self.inputs['Update FITS Header'].grid(row=2, column=0, columnspan=3)

        # Line 4
        self.inputs['FITS Header Filter'] = w.LabelInput(
                ScienceDetails, "FITS Header Filter",
                field_spec=fields['science_details']['fits_header_filter'],
                label_args={'style':'ScienceDetails.TLabel'})
        self.inputs['FITS Header Filter'].grid(row=3, column=0)

        self.inputs['Filename Filter Text'] = w.LabelInput(
                ScienceDetails, "Filename Filter Text",
                field_spec=fields['science_details']['filename_text_filter'],
                label_args={'style':'ScienceDetails.TLabel'})
        self.inputs['Filename Filter Text'].grid(row=3, column=1)

        #Line 5
        self.inputs['Use FITS Filter'] = w.LabelInput(
                ScienceDetails, "Use FITS Filter",
                field_spec=fields['science_details']['use_fits_filter'],
                label_args={'style':'ScienceDetails.TLabel'},
                input_args={'style':'ScienceDetails.TCheckbutton'})
        self.inputs['Use FITS Filter'].grid(row=4, column=0, columnspan=1)

        self.inputs['Use Filename Filter'] = w.LabelInput(
                ScienceDetails, "Use Filename Filter",
                field_spec=fields['science_details']['use_filename_filter'],
                label_args={'style':'ScienceDetails.TLabel'},
                input_args={'style':'ScienceDetails.TCheckbutton'})
        self.inputs['Use Filename Filter'].grid(row=4, column=1, columnspan=1)

        #Line 6
        self.inputs['Update FITS Header Filter'] = w.LabelInput(
                ScienceDetails, "Update FITS Header Filter",
                field_spec=fields['science_details']['update_fits_filter'],
                label_args={'style':'ScienceDetails.TLabel'},
                input_args={'style':'ScienceDetails.TCheckbutton'})
        self.inputs['Update FITS Header Filter'].grid(row=5, column=0, columnspan=3)

        ScienceDetails.grid(row=2, column=1, sticky=tk.W + tk.E)

        # Master Details
        MasterDetails = tk.LabelFrame(self, 
                                   text="Master Details",
                                   bg="lightgreen",
                                   padx=10,
                                   pady=10
                                   )
        
        # Line 1
        self.inputs['Filename Master Bias'] = w.LabelInput(
                MasterDetails, "Filename Master Bias",
                field_spec=fields['master_details']['filename_bias'],
                label_args={'style':'MasterDetails.TLabel'})
        self.inputs['Filename Master Bias'].grid(row=0, column=0)

        self.inputs['Filename Master Dark'] = w.LabelInput(
                MasterDetails, "Filename Master Dark",
                field_spec=fields['master_details']['filename_dark'],
                label_args={'style':'MasterDetails.TLabel'})
        self.inputs['Filename Master Dark'].grid(row=0, column=1)

        self.inputs['Filename Master Flat'] = w.LabelInput(
                MasterDetails, "Filename Master Flat",
                field_spec=fields['master_details']['filename_flat'],
                label_args={'style':'MasterDetails.TLabel'})
        self.inputs['Filename Master Flat'].grid(row=0, column=2)
       
        # Line 2
        self.inputs['FITS Header Image'] = w.LabelInput(
                MasterDetails, "FITS Header Image",
                field_spec=fields['master_details']['fits_header_image'],
                label_args={'style':'MasterDetails.TLabel'})
        self.inputs['FITS Header Image'].grid(row=1, column=0)

        # Line 3
        self.inputs['FITS Header Image Value Bias'] = w.LabelInput(
                MasterDetails, "FITS Header Image Value Bias",
                field_spec=fields['master_details']['fits_header_image_value_bias'],
                label_args={'style':'MasterDetails.TLabel'})
        self.inputs['FITS Header Image Value Bias'].grid(row=2, column=0)

        self.inputs['FITS Header Image Value Dark'] = w.LabelInput(
                MasterDetails, "FITS Header Image Value Dark",
                field_spec=fields['master_details']['fits_header_image_value_dark'],
                label_args={'style':'MasterDetails.TLabel'})
        self.inputs['FITS Header Image Value Dark'].grid(row=2, column=1)

        self.inputs['FITS Header Image Value Flat'] = w.LabelInput(
                MasterDetails, "FITS Header Image Value Flat",
                field_spec=fields['master_details']['fits_header_image_value_flat'],
                label_args={'style':'MasterDetails.TLabel'})
        self.inputs['FITS Header Image Value Flat'].grid(row=2, column=2)

        #Line 4
        self.inputs['Update FITS Header'] = w.LabelInput(
                MasterDetails, "Update FITS Header",
                field_spec=fields['master_details']['update_fits'],
                label_args={'style':'MasterDetails.TLabel'},
                input_args={'style':'MasterDetails.TCheckbutton'})
        self.inputs['Update FITS Header'].grid(row=3, column=0, columnspan=3)
        
        MasterDetails.grid(row=0, column=2, sticky=tk.W + tk.E)

        # Reduction Details
        ReductionDetails = tk.LabelFrame(self, 
                                   text="Reduction Details",
                                   bg="lightgreen",
                                   padx=10,
                                   pady=10
                                   )
        
        # Line 1
        self.inputs['Filename Bias Stub'] = w.LabelInput(
                ReductionDetails, "Filename Master Bias",
                field_spec=fields['reduction_details']['filename_bias_stub'],
                label_args={'style':'ReductionDetails.TLabel'})
        self.inputs['Filename Bias Stub'].grid(row=0, column=0)

        # Line 2
        self.inputs['Filename Bias Prefix'] = w.LabelInput(
                ReductionDetails, "Filename Bias Prefix",
                field_spec=fields['reduction_details']['filename_bias_prefix'],
                label_args={'style':'ReductionDetails.TLabel'},
                input_args={'style':'ReductionDetails.TCheckbutton'})
        self.inputs['Filename Bias Prefix'].grid(row=1, column=0, columnspan=1)

        self.inputs['Filename Bias Suffix'] = w.LabelInput(
                ReductionDetails, "Filename Bias Suffix",
                field_spec=fields['reduction_details']['filename_bias_suffix'],
                label_args={'style':'ReductionDetails.TLabel'},
                input_args={'style':'ReductionDetails.TCheckbutton'})
        self.inputs['Filename Bias Suffix'].grid(row=1, column=1, columnspan=1)

        # Line 3
        self.inputs['Filename Dark Stub'] = w.LabelInput(
                ReductionDetails, "Filename Master Dark",
                field_spec=fields['reduction_details']['filename_dark_stub'],
                label_args={'style':'ReductionDetails.TLabel'})
        self.inputs['Filename Dark Stub'].grid(row=2, column=0)

        # Line 4
        self.inputs['Filename Dark Prefix'] = w.LabelInput(
                ReductionDetails, "Filename Dark Prefix",
                field_spec=fields['reduction_details']['filename_dark_prefix'],
                label_args={'style':'ReductionDetails.TLabel'},
                input_args={'style':'ReductionDetails.TCheckbutton'})
        self.inputs['Filename Dark Prefix'].grid(row=3, column=0, columnspan=1)

        self.inputs['Filename Dark Suffix'] = w.LabelInput(
                ReductionDetails, "Filename Dark Suffix",
                field_spec=fields['reduction_details']['filename_dark_suffix'],
                label_args={'style':'ReductionDetails.TLabel'},
                input_args={'style':'ReductionDetails.TCheckbutton'})
        self.inputs['Filename Dark Suffix'].grid(row=3, column=1, columnspan=1)

        # Line 5
        self.inputs['Filename Flat Stub'] = w.LabelInput(
                ReductionDetails, "Filename Master Flat",
                field_spec=fields['reduction_details']['filename_flat_stub'],
                label_args={'style':'ReductionDetails.TLabel'})
        self.inputs['Filename Flat Stub'].grid(row=4, column=0)

        # Line 6
        self.inputs['Filename Flat Prefix'] = w.LabelInput(
                ReductionDetails, "Filename Flat Prefix",
                field_spec=fields['reduction_details']['filename_flat_prefix'],
                label_args={'style':'ReductionDetails.TLabel'},
                input_args={'style':'ReductionDetails.TCheckbutton'})
        self.inputs['Filename Flat Prefix'].grid(row=5, column=0, columnspan=1)

        self.inputs['Filename Flat Suffix'] = w.LabelInput(
                ReductionDetails, "Filename Flat Suffix",
                field_spec=fields['reduction_details']['filename_flat_suffix'],
                label_args={'style':'ReductionDetails.TLabel'},
                input_args={'style':'ReductionDetails.TCheckbutton'})
        self.inputs['Filename Flat Suffix'].grid(row=5, column=1, columnspan=1)

        # Line 7
        self.inputs['Filename Reduced Stub'] = w.LabelInput(
                ReductionDetails, "Filename Master Reduced",
                field_spec=fields['reduction_details']['filename_reduced_stub'],
                label_args={'style':'ReductionDetails.TLabel'})
        self.inputs['Filename Reduced Stub'].grid(row=6, column=0)

        # Line 8
        self.inputs['Filename Reduced Prefix'] = w.LabelInput(
                ReductionDetails, "Filename Reduced Prefix",
                field_spec=fields['reduction_details']['filename_reduced_prefix'],
                label_args={'style':'ReductionDetails.TLabel'},
                input_args={'style':'ReductionDetails.TCheckbutton'})
        self.inputs['Filename Reduced Prefix'].grid(row=7, column=0, columnspan=1)

        self.inputs['Filename Reduced Suffix'] = w.LabelInput(
                ReductionDetails, "Filename Reduced Suffix",
                field_spec=fields['reduction_details']['filename_reduced_suffix'],
                label_args={'style':'ReductionDetails.TLabel'},
                input_args={'style':'ReductionDetails.TCheckbutton'})
        self.inputs['Filename Reduced Suffix'].grid(row=7, column=1, columnspan=1)

        # Line 9
        self.inputs['Filename Stub Modifier'] = w.LabelInput(
                ReductionDetails, "Filename Stub Modifier",
                field_spec=fields['reduction_details']['filename_prefix_suffix_modifier'],
                label_args={'style':'ReductionDetails.TLabel'})
        self.inputs['Filename Stub Modifier'].grid(row=8, column=0)

        ReductionDetails.grid(row=2, column=2, sticky=tk.W + tk.E)
        
        """# Notes Section
        self.inputs['Notes'] = w.LabelInput(
                self, "Notes",
                field_spec=fields['Notes'])
        self.inputs['Notes'].grid(sticky="w", row=4, column=0, padx=10, pady=10)"""
        
        """# Save button
        self.savebutton = ttk.Button(self,
                                     text="Save",
                                     command=self.callbacks["on_save"],
                                     )
        self.savebutton.grid(sticky="e",row=5,padx=10)"""
 
        self.reset()
        
    def get(self):
        data = {}
        for key, widget in self.inputs.items():
            data[key] = widget.get()
        return data
    
    def reset(self):
        """Resets the form entries"""
        pass
        """#gather the values to keep for each lab
        lab = self.inputs['Lab'].get()
        time = self.inputs['Time'].get()
        technician = self.inputs['Technician'].get()
        plot = self.inputs['Plot'].get()
        plot_values = self.inputs['Plot'].input.cget('values')
        
        #clear all values
        for widget in self.inputs.values():
            widget.set('')
            
        current_date = datetime.today().strftime('%Y-%m-%d')
        self.inputs['Date'].set(current_date)
        self.inputs['Time'].input.focus()
        
        #check if we need to put our values back
        
        if plot not in ('',plot_values[-1]):
            self.inputs['Lab'].set(lab)
            self.inputs['Time'].set(time)
            self.inputs['Technician'].set(technician)
            next_plot_index = plot_values.index(plot)+1
            self.inputs['Plot'].set(plot_values[next_plot_index])
            self.inputs['Seed sample'].input.focus()"""
            
    def get_errors(self):
        """Get a list of field errors in the form"""
        errors={}
        
        """for key, widget in self.inputs.items():
            if hasattr(widget.input, 'trigger_focusout_validation'):
                widget.input.trigger_focusout_validation()
            if widget.error.get():
                errors[key] = widget.error.get()"""
            
        return errors
    
    def load_record(self,rownum,data=None):
        self.current_record = rownum
        
        """if rownum is None:
            self.reset()
            self.record_label.config(text='New Record')
        else:
            self.record_label.config(text='Record #{}'.format(rownum))
            for key,widget in self.inputs.items():
                self.inputs[key].set(data.get(key,''))
                try:
                    widget.input.trigger_focusout_validation()
                except AttributeError:
                    pass"""

class DirectoriesConfigurationForm(tk.Frame):
    """The directories configuration form"""
    
    def __init__(self, parent, fields, settings, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.settings = settings
        self.callbacks = callbacks
        
        self.current_record = None
        # A dict to keep track of input widgets
        self.inputs = {}
        
        # Styles
        style = ttk.Style()
        
        style.configure('Directories.TLabel',background='khaki')
        style.configure('Directories.TCheckbutton',background='khaki')
        
        # Directories
        Directories = tk.LabelFrame(self, 
                                   text="Directories",
                                   bg="Khaki",
                                   padx=10,
                                   pady=10
                                   )
        
        # Line 1
        self.inputs['Source'] = w.LabelInput(
                Directories, "Source",
                field_spec=fields['source_dir'],
                label_args={'style':'Directories.TLabel'})
        self.inputs['Source'].grid(row=0, column=0)

        self.inputs['Science'] = w.LabelInput(
                Directories, "Science",
                field_spec=fields['science_dir'],
                label_args={'style':'Directories.TLabel'})
        self.inputs['Science'].grid(row=0, column=1)

        self.inputs['Masters'] = w.LabelInput(
                Directories, "Masters",
                field_spec=fields['master_dir'],
                label_args={'style':'Directories.TLabel'})
        self.inputs['Masters'].grid(row=0, column=2)
       
        # Line 2
        self.inputs['Bias'] = w.LabelInput(
                Directories, "Bias",
                field_spec=fields['bias_dir'],
                label_args={'style':'Directories.TLabel'})
        self.inputs['Bias'].grid(row=1, column=0)

        self.inputs['Dark'] = w.LabelInput(
                Directories, "Dark",
                field_spec=fields['dark_dir'],
                label_args={'style':'Directories.TLabel'})
        self.inputs['Dark'].grid(row=1, column=1)

        self.inputs['Flat'] = w.LabelInput(
                Directories, "Flat",
                field_spec=fields['flat_dir'],
                label_args={'style':'Directories.TLabel'})
        self.inputs['Flat'].grid(row=1, column=2)

        # Line 3
        self.inputs['Working'] = w.LabelInput(
                Directories, "Working",
                field_spec=fields['working_dir'],
                label_args={'style':'Directories.TLabel'})
        self.inputs['Working'].grid(row=2, column=0)

        self.inputs['Output'] = w.LabelInput(
                Directories, "Output",
                field_spec=fields['output_dir'],
                label_args={'style':'Directories.TLabel'})
        self.inputs['Output'].grid(row=2, column=1)

        #Line 4
        self.inputs['Save Masters'] = w.LabelInput(
                Directories, "Save Masters",
                field_spec=fields['save_masters'],
                label_args={'style':'Directories.TLabel'},
                input_args={'style':'Directories.TCheckbutton'})
        self.inputs['Save Masters'].grid(row=3, column=0, columnspan=3)

        #Line 5
        self.inputs['Save Working'] = w.LabelInput(
                Directories, "Save Working",
                field_spec=fields['save_working'],
                label_args={'style':'Directories.TLabel'},
                input_args={'style':'Directories.TCheckbutton'})
        self.inputs['Save Working'].grid(row=4, column=0, columnspan=3)
        
        Directories.grid(row=0, column=0, sticky=tk.W + tk.E)
 
        self.reset()
        
    def get(self):
        data = {}
        for key, widget in self.inputs.items():
            data[key] = widget.get()
        return data
    
    def reset(self):
        """Resets the form entries"""
        pass
            
    def get_errors(self):
        """Get a list of field errors in the form"""
        errors={}
        
        """for key, widget in self.inputs.items():
            if hasattr(widget.input, 'trigger_focusout_validation'):
                widget.input.trigger_focusout_validation()
            if widget.error.get():
                errors[key] = widget.error.get()"""
            
        return errors
    
    def populate_form(self,fields):
        """ Populate Form"""

        self.inputs['Source'].set(fields['source_dir'])
        self.inputs['Science'].set(fields['science_dir'])
        self.inputs['Masters'].set(fields['master_dir'])
        self.inputs['Bias'].set(fields['bias_dir'])
        self.inputs['Dark'].set(fields['dark_dir'])
        self.inputs['Flat'].set(fields['flat_dir'])
        self.inputs['Working'].set(fields['working_dir'])
        self.inputs['Output'].set(fields['output_dir'])
        self.inputs['Save Masters'].set(fields.as_bool('save_masters'))
        self.inputs['Save Working'].set(fields.as_bool('save_working'))

    def save_form(self,fields):
        """ Save Form"""

        fields['source_dir'] = self.inputs['Source'].get()
        fields['science_dir'] = self.inputs['Science'].get()
        fields['master_dir'] = self.inputs['Masters'].get()
        fields['bias_dir'] = self.inputs['Bias'].get()
        fields['dark_dir'] = self.inputs['Dark'].get()
        fields['flat_dir'] = self.inputs['Flat'].get()
        fields['working_dir'] = self.inputs['Working'].get()
        fields['output_dir'] = self.inputs['Output'].get()
        fields['save_masters'] = self.inputs['Save Masters'].get()
        fields['save_working'] =self.inputs['Save Working'].get()

        return fields

class GeneralConfigurationForm(tk.Frame):
    """The general configuration form"""
    
    def __init__(self, parent, fields, settings, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.settings = settings
        self.callbacks = callbacks
        
        self.current_record = None
        # A dict to keep track of input widgets
        self.inputs = {}
        
        # Styles
        style = ttk.Style()
        
        style.configure('GeneralDetails.TLabel',background='lightblue')
        style.configure('GeneralDetails.TCheckbutton',background='lightblue')
         
        # General Details
        GeneralDetails = tk.LabelFrame(self, 
                                   text="General Details",
                                   bg="lightblue",
                                   padx=10,
                                   pady=10
                                   )
        
        # Line 1
        self.inputs['FITS Header Image Type'] = w.LabelInput(
                GeneralDetails, "FITS Header Image Type",
                field_spec=fields['fits_header_image_type'],
                label_args={'style':'GeneralDetails.TLabel'})
        self.inputs['FITS Header Image Type'].grid(row=0, column=0)

        self.inputs['FITS Header Filter'] = w.LabelInput(
                GeneralDetails, "FITS Header Filter",
                field_spec=fields['fits_header_filter'],
                label_args={'style':'GeneralDetails.TLabel'})
        self.inputs['FITS Header Filter'].grid(row=0, column=1)

        # Line 2
        self.inputs['FITS Header Exposure'] = w.LabelInput(
                GeneralDetails, "FITS Header Exposure",
                field_spec=fields['fits_header_exposure'],
                label_args={'style':'GeneralDetails.TLabel'})
        self.inputs['FITS Header Exposure'].grid(row=1, column=0)

        self.inputs['FITS Header CCD Temp'] = w.LabelInput(
                GeneralDetails, "FITS Header CCD Temp",
                field_spec=fields['fits_header_CCD_Temp'],
                label_args={'style':'GeneralDetails.TLabel'})
        self.inputs['FITS Header CCD Temp'].grid(row=1, column=1)

        GeneralDetails.grid(row=0, column=0, sticky=tk.W + tk.E)
 
        self.reset()
        
    def get(self):
        data = {}
        for key, widget in self.inputs.items():
            data[key] = widget.get()
        return data
    
    def reset(self):
        """Resets the form entries"""
        pass
            
    def get_errors(self):
        """Get a list of field errors in the form"""
        errors={}
        
        """for key, widget in self.inputs.items():
            if hasattr(widget.input, 'trigger_focusout_validation'):
                widget.input.trigger_focusout_validation()
            if widget.error.get():
                errors[key] = widget.error.get()"""
            
        return errors
    
    def populate_form(self,fields):
        """ Populate Form"""
        
        self.inputs['FITS Header Image Type'].set(fields['fits_header_image_type'])
        self.inputs['FITS Header Filter'].set(fields['fits_header_filter'])
        self.inputs['FITS Header Exposure'].set(fields['fits_header_exposure'])
        self.inputs['FITS Header CCD Temp'].set(fields['fits_header_CCD_temp'])

    def save_form(self,fields):
        """ Save Form"""

        fields['fits_header_image_type'] = self.inputs['FITS Header Image Type'].get()
        fields['fits_header_filter'] = self.inputs['FITS Header Filter'].get()
        fields['fits_header_exposure'] = self.inputs['FITS Header Exposure'].get()
        fields['fits_header_CCD_temp'] = self.inputs['FITS Header CCD Temp'].get()

        return fields

class BiasDetailsConfigurationForm(tk.Frame):
    """The bias details configuration form"""
    
    def __init__(self, parent, fields, settings, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.settings = settings
        self.callbacks = callbacks
        
        self.current_record = None
        # A dict to keep track of input widgets
        self.inputs = {}
        
        # Styles
        style = ttk.Style()
        
        style.configure('BiasDetails.TLabel',background='lightgreen')
        style.configure('BiasDetails.TCheckbutton',background='lightgreen')
        style.configure('BiasDetails.TRadiobutton',background='lightgreen')
        
        # Bias Details
        BiasDetails = tk.LabelFrame(self, 
                                   text="Bias Details",
                                   bg="lightgreen",
                                   padx=10,
                                   pady=10
                                   )
        
        # Line 1
        
        self.inputs['FITS Header Value'] = w.LabelInput(
                BiasDetails, "FITS Header Value",
                field_spec=fields['fits_header_image_value'],
                label_args={'style':'BiasDetails.TLabel'})
        self.inputs['FITS Header Value'].grid(row=0, column=0)

        self.inputs['Filename Text'] = w.LabelInput(
                BiasDetails, "Filename Text",
                field_spec=fields['filename_text'],
                label_args={'style':'BiasDetails.TLabel'})
        self.inputs['Filename Text'].grid(row=0, column=1)

        #Line 2
        self.use_fits_radiobutton = tk.StringVar()
        self.inputs['Use FITS Header'] = w.LabelInput(
                BiasDetails, "Use FITS Header",
                input_var=self.use_fits_radiobutton, 
                field_spec=fields['use_fits'],
                label_args={'style':'BiasDetails.TLabel'},
                input_args={'style':'BiasDetails.TRadiobutton',
                                'variable':'self.use_fits_radiobutton',
                                'value' : 'True'})
        self.inputs['Use FITS Header'].grid(row=1, column=0, columnspan=1)

        self.inputs['Use Filename'] = w.LabelInput(
                BiasDetails, "Use Filename",
                input_var=self.use_fits_radiobutton, 
                field_spec=fields['use_fits'],
                label_args={'style':'BiasDetails.TLabel'},
                input_args={'style':'BiasDetails.TRadiobutton',
                                'variable':'self.use_fits_radiobutton',
                                'value' : 'False'})
        self.inputs['Use Filename'].grid(row=1, column=1, columnspan=1)

        #Line 3
        self.inputs['Update FITS Header'] = w.LabelInput(
                BiasDetails, "Update FITS Header",
                field_spec=fields['update_fits'],
                label_args={'style':'BiasDetails.TLabel'},
                input_args={'style':'BiasDetails.TCheckbutton'})
        self.inputs['Update FITS Header'].grid(row=2, column=0, columnspan=3)

        BiasDetails.grid(row=0, column=0, sticky=tk.W + tk.E)
 
        self.reset()
        
    def get(self):
        data = {}
        for key, widget in self.inputs.items():
            data[key] = widget.get()
        return data
    
    def reset(self):
        """Resets the form entries"""
        pass
            
    def get_errors(self):
        """Get a list of field errors in the form"""
        errors={}
        
        """for key, widget in self.inputs.items():
            if hasattr(widget.input, 'trigger_focusout_validation'):
                widget.input.trigger_focusout_validation()
            if widget.error.get():
                errors[key] = widget.error.get()"""
            
        return errors
    
    def populate_form(self,fields):
        """ Populate Form"""
        
        self.inputs['FITS Header Value'].set(fields['fits_header_image_value'])
        self.inputs['Filename Text'].set(fields['filename_text'])
        self.inputs['Use FITS Header'].set(fields['use_fits'])
        self.inputs['Update FITS Header'].set(fields.as_bool('update_fits'))

    def save_form(self,fields):
        """ Save Form"""

        fields['fits_header_image_value'] = self.inputs['FITS Header Value'].get()
        fields['filename_text'] = self.inputs['Filename Text'].get()
        fields['use_fits'] = self.inputs['Use FITS Header'].get()
        fields['update_fits'] = self.inputs['Update FITS Header'].get()

        return fields

class DarkDetailsConfigurationForm(tk.Frame):
    """The dark details configuration form"""
    
    def __init__(self, parent, fields, settings, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.settings = settings
        self.callbacks = callbacks
        
        self.current_record = None
        # A dict to keep track of input widgets
        self.inputs = {}
        
        # Styles
        style = ttk.Style()
        
        style.configure('DarkDetails.TLabel',background='lightgreen')
        style.configure('DarkDetails.TCheckbutton',background='lightgreen')
        style.configure('DarkDetails.TRadiobutton',background='lightgreen')
        
        # Dark Details
        DarkDetails = tk.LabelFrame(self, 
                                   text="Dark Details",
                                   bg="lightgreen",
                                   padx=10,
                                   pady=10
                                   )
        
        # Line 1
        self.inputs['FITS Header Value'] = w.LabelInput(
                DarkDetails, "FITS Header Value",
                field_spec=fields['fits_header_image_value'],
                label_args={'style':'DarkDetails.TLabel'})
        self.inputs['FITS Header Value'].grid(row=0, column=0)

        self.inputs['Filename Text'] = w.LabelInput(
                DarkDetails, "Filename Text",
                field_spec=fields['filename_text'],
                label_args={'style':'DarkDetails.TLabel'})
        self.inputs['Filename Text'].grid(row=0, column=1)

        #Line 2
        self.use_fits_radiobutton = tk.StringVar()
        self.inputs['Use FITS Header'] = w.LabelInput(
                DarkDetails, "Use FITS Header",
                input_var=self.use_fits_radiobutton, 
                field_spec=fields['use_fits'],
                label_args={'style':'DarkDetails.TLabel'},
                input_args={'style':'DarkDetails.TRadiobutton',
                                'variable':'self.use_fits_radiobutton',
                                'value' : 'True'})
        self.inputs['Use FITS Header'].grid(row=1, column=0, columnspan=1)

        self.inputs['Use Filename'] = w.LabelInput(
                DarkDetails, "Use Filename",
                input_var=self.use_fits_radiobutton, 
                field_spec=fields['use_fits'],
                label_args={'style':'DarkDetails.TLabel'},
                input_args={'style':'DarkDetails.TRadiobutton',
                                'variable':'self.use_fits_radiobutton',
                                'value' : 'False'})
        self.inputs['Use Filename'].grid(row=1, column=1, columnspan=1)

        #Line 3
        self.inputs['Update FITS Header'] = w.LabelInput(
                DarkDetails, "Update FITS Header",
                field_spec=fields['update_fits'],
                label_args={'style':'DarkDetails.TLabel'},
                input_args={'style':'DarkDetails.TCheckbutton'})
        self.inputs['Update FITS Header'].grid(row=2, column=0, columnspan=1)

        DarkDetails.grid(row=0, column=0, sticky=tk.W + tk.E)
 
        self.reset()
        
    def get(self):
        data = {}
        for key, widget in self.inputs.items():
            data[key] = widget.get()
        return data
    
    def reset(self):
        """Resets the form entries"""
        pass

            
    def get_errors(self):
        """Get a list of field errors in the form"""
        errors={}
        
        """for key, widget in self.inputs.items():
            if hasattr(widget.input, 'trigger_focusout_validation'):
                widget.input.trigger_focusout_validation()
            if widget.error.get():
                errors[key] = widget.error.get()"""
            
        return errors
    
    def populate_form(self,fields):
        """ Populate Form"""
        
        self.inputs['FITS Header Value'].set(fields['fits_header_image_value'])
        self.inputs['Filename Text'].set(fields['filename_text'])
        self.inputs['Use FITS Header'].set(fields['use_fits'])
        self.inputs['Update FITS Header'].set(fields.as_bool('update_fits'))

    def save_form(self,fields):
        """ Save Form"""

        fields['fits_header_image_value'] = self.inputs['FITS Header Value'].get()
        fields['filename_text'] = self.inputs['Filename Text'].get()
        fields['use_fits'] = self.inputs['Use FITS Header'].get()
        fields['update_fits'] = self.inputs['Update FITS Header'].get()

        return fields

class FlatDetailsConfigurationForm(tk.Frame):
    """The flat details configuration form"""
    
    def __init__(self, parent, fields, settings, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.settings = settings
        self.callbacks = callbacks
        
        self.current_record = None
        # A dict to keep track of input widgets
        self.inputs = {}
        
        # Styles
        style = ttk.Style()
        
        style.configure('FlatDetails.TLabel',background='lightgreen')
        style.configure('FlatDetails.TCheckbutton',background='lightgreen')
        style.configure('FlatDetails.TRadiobutton',background='lightgreen')
        
        # Flat Details
        FlatDetails = tk.LabelFrame(self, 
                                   text="Flat Details",
                                   bg="lightgreen",
                                   padx=10,
                                   pady=10
                                   )
        
        # Line 1
        self.inputs['FITS Header Value'] = w.LabelInput(
                FlatDetails, "FITS Header Value",
                field_spec=fields['fits_header_image_value'],
                label_args={'style':'FlatDetails.TLabel'})
        self.inputs['FITS Header Value'].grid(row=0, column=0)

        self.inputs['Filename Text'] = w.LabelInput(
                FlatDetails, "Filename Text",
                field_spec=fields['filename_text'],
                label_args={'style':'FlatDetails.TLabel'})
        self.inputs['Filename Text'].grid(row=0, column=1)

        #Line 2
        self.use_fits_radiobutton = tk.StringVar()
        self.inputs['Use FITS Header'] = w.LabelInput(
                FlatDetails, "Use FITS Header",
                input_var=self.use_fits_radiobutton, 
                field_spec=fields['use_fits'],
                label_args={'style':'FlatDetails.TLabel'},
                input_args={'style':'FlatDetails.TRadiobutton',
                                'variable':'self.use_fits_radiobutton',
                                'value' : 'True'})
        self.inputs['Use FITS Header'].grid(row=1, column=0, columnspan=1)

        self.inputs['Use Filename'] = w.LabelInput(
                FlatDetails, "Use Filename",
                input_var=self.use_fits_radiobutton, 
                field_spec=fields['use_fits'],
                label_args={'style':'FlatDetails.TLabel'},
                input_args={'style':'FlatDetails.TRadiobutton',
                                'variable':'self.use_fits_radiobutton',
                                'value' : 'False'})
        self.inputs['Use Filename'].grid(row=1, column=1, columnspan=1)

        #Line 3
        self.inputs['Update FITS Header'] = w.LabelInput(
                FlatDetails, "Update FITS Header",
                field_spec=fields['update_fits'],
                label_args={'style':'FlatDetails.TLabel'},
                input_args={'style':'FlatDetails.TCheckbutton'})
        self.inputs['Update FITS Header'].grid(row=2, column=0, columnspan=3)

        # Line 4
        self.inputs['Filename Filter Text'] = w.LabelInput(
                FlatDetails, "Filename Filter Text",
                field_spec=fields['filename_text_filter'],
                label_args={'style':'FlatDetails.TLabel'})
        self.inputs['Filename Filter Text'].grid(row=3, column=0)

        #Line 5
        self.use_fits_filter_radiobutton = tk.StringVar()
        self.inputs['Use FITS Header Filter'] = w.LabelInput(
                FlatDetails, "Use FITS Header Filter",
                input_var=self.use_fits_filter_radiobutton, 
                field_spec=fields['use_fits_filter'],
                label_args={'style':'FlatDetails.TLabel'},
                input_args={'style':'FlatDetails.TRadiobutton',
                                'variable':'self.use_fits_filter_radiobutton',
                                'value' : 'True'})
        self.inputs['Use FITS Header Filter'].grid(row=4, column=0, columnspan=1)

        self.inputs['Use Filename Filter'] = w.LabelInput(
                FlatDetails, "Use Filename Filter",
                input_var=self.use_fits_filter_radiobutton, 
                field_spec=fields['use_fits_filter'],
                label_args={'style':'FlatDetails.TLabel'},
                input_args={'style':'FlatDetails.TRadiobutton',
                                'variable':'self.use_fits_filter_radiobutton',
                                'value' : 'False'})
        self.inputs['Use Filename Filter'].grid(row=4, column=1, columnspan=1)

        #Line 6
        self.inputs['Update FITS Header Filter'] = w.LabelInput(
                FlatDetails, "Update FITS Header Filter",
                field_spec=fields['update_fits_filter'],
                label_args={'style':'FlatDetails.TLabel'},
                input_args={'style':'FlatDetails.TCheckbutton'})
        self.inputs['Update FITS Header Filter'].grid(row=5, column=0, columnspan=3)

        FlatDetails.grid(row=0, column=0, sticky=tk.W + tk.E)
 
        self.reset()
        
    def get(self):
        data = {}
        for key, widget in self.inputs.items():
            data[key] = widget.get()
        return data
    
    def reset(self):
        """Resets the form entries"""
        pass
            
    def get_errors(self):
        """Get a list of field errors in the form"""
        errors={}
        
        """for key, widget in self.inputs.items():
            if hasattr(widget.input, 'trigger_focusout_validation'):
                widget.input.trigger_focusout_validation()
            if widget.error.get():
                errors[key] = widget.error.get()"""
            
        return errors
    
    def populate_form(self,fields):
        """ Populate Form"""
        
        self.inputs['FITS Header Value'].set(fields['fits_header_image_value'])
        self.inputs['Filename Text'].set(fields['filename_text'])
        self.inputs['Use FITS Header'].set(fields['use_fits'])
        self.inputs['Update FITS Header'].set(fields.as_bool('update_fits'))
        self.inputs['Filename Filter Text'].set(fields['filename_text_filter'])
        self.inputs['Use FITS Header Filter'].set(fields['use_fits_filter'])
        self.inputs['Update FITS Header Filter'].set(fields.as_bool('update_fits_filter'))

    def save_form(self,fields):
        """ Save Form"""

        fields['fits_header_image_value'] = self.inputs['FITS Header Value'].get()
        fields['filename_text'] = self.inputs['Filename Text'].get()
        fields['use_fits'] = self.inputs['Use FITS Header'].get()
        fields['update_fits'] = self.inputs['Update FITS Header'].get()
        fields['filename_text_filter'] = self.inputs['Filename Filter Text'].get()
        fields['use_fits_filter'] = self.inputs['Use FITS Header Filter'].get()
        fields['update_fits_filter'] = self.inputs['Update FITS Header Filter'].get()

        return fields

class ScienceDetailsConfigurationForm(tk.Frame):
    """The science details configuration form"""
    
    def __init__(self, parent, fields, settings, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.settings = settings
        self.callbacks = callbacks
        
        self.current_record = None
        # A dict to keep track of input widgets
        self.inputs = {}
        
        # Styles
        style = ttk.Style()
        
        style.configure('ScienceDetails.TLabel',background='lightgreen')
        style.configure('ScienceDetails.TCheckbutton',background='lightgreen')
        style.configure('ScienceDetails.TRadiobutton',background='lightgreen')
        
        # Science Details
        ScienceDetails = tk.LabelFrame(self, 
                                   text="Science Details",
                                   bg="lightgreen",
                                   padx=10,
                                   pady=10
                                   )
        
        # Line 1
        self.inputs['FITS Header Value'] = w.LabelInput(
                ScienceDetails, "FITS Header Value",
                field_spec=fields['fits_header_image_value'],
                label_args={'style':'ScienceDetails.TLabel'})
        self.inputs['FITS Header Value'].grid(row=0, column=0)

        self.inputs['Filename Text'] = w.LabelInput(
                ScienceDetails, "Filename Text",
                field_spec=fields['filename_text'],
                label_args={'style':'ScienceDetails.TLabel'})
        self.inputs['Filename Text'].grid(row=0, column=1)

        #Line 2
        self.use_fits_radiobutton = tk.StringVar()
        self.inputs['Use FITS Header'] = w.LabelInput(
                ScienceDetails, "Use FITS Header",
                input_var=self.use_fits_radiobutton, 
                field_spec=fields['use_fits'],
                label_args={'style':'ScienceDetails.TLabel'},
                input_args={'style':'ScienceDetails.TRadiobutton',
                                'variable':'self.use_fits_radiobutton',
                                'value' : 'True'})
        self.inputs['Use FITS Header'].grid(row=1, column=0, columnspan=1)

        self.inputs['Use Filename'] = w.LabelInput(
                ScienceDetails, "Use Filename",
                input_var=self.use_fits_radiobutton, 
                field_spec=fields['use_fits'],
                label_args={'style':'ScienceDetails.TLabel'},
                input_args={'style':'ScienceDetails.TRadiobutton',
                                'variable':'self.use_fits_radiobutton',
                                'value' : 'False'})
        self.inputs['Use Filename'].grid(row=1, column=1, columnspan=1)

        #Line 3
        self.inputs['Update FITS Header'] = w.LabelInput(
                ScienceDetails, "Update FITS Header",
                field_spec=fields['update_fits'],
                label_args={'style':'ScienceDetails.TLabel'},
                input_args={'style':'ScienceDetails.TCheckbutton'})
        self.inputs['Update FITS Header'].grid(row=2, column=0, columnspan=3)

        # Line 4
        self.inputs['Filename Filter Text'] = w.LabelInput(
                ScienceDetails, "Filename Filter Text",
                field_spec=fields['filename_text_filter'],
                label_args={'style':'ScienceDetails.TLabel'})
        self.inputs['Filename Filter Text'].grid(row=3, column=0)

        #Line 5
        self.use_fits_filter_radiobutton = tk.StringVar()
        self.inputs['Use FITS Header Filter'] = w.LabelInput(
                ScienceDetails, "Use FITS Header Filter",
                input_var=self.use_fits_filter_radiobutton, 
                field_spec=fields['use_fits_filter'],
                label_args={'style':'ScienceDetails.TLabel'},
                input_args={'style':'ScienceDetails.TRadiobutton',
                                'variable':'self.use_fits_filter_radiobutton',
                                'value' : 'True'})
        self.inputs['Use FITS Header Filter'].grid(row=4, column=0, columnspan=1)

        self.inputs['Use Filename Filter'] = w.LabelInput(
                ScienceDetails, "Use Filename Filter",
                input_var=self.use_fits_filter_radiobutton, 
                field_spec=fields['use_fits_filter'],
                label_args={'style':'ScienceDetails.TLabel'},
                input_args={'style':'ScienceDetails.TRadiobutton',
                                'variable':'self.use_fits_filter_radiobutton',
                                'value' : 'False'})
        self.inputs['Use Filename Filter'].grid(row=4, column=1, columnspan=1)

        #Line 6
        self.inputs['Update FITS Header Filter'] = w.LabelInput(
                ScienceDetails, "Update FITS Header Filter",
                field_spec=fields['update_fits_filter'],
                label_args={'style':'ScienceDetails.TLabel'},
                input_args={'style':'ScienceDetails.TCheckbutton'})
        self.inputs['Update FITS Header Filter'].grid(row=5, column=0, columnspan=3)

        ScienceDetails.grid(row=0, column=0, sticky=tk.W + tk.E)
 
        self.reset()
        
    def get(self):
        data = {}
        for key, widget in self.inputs.items():
            data[key] = widget.get()
        return data
    
    def reset(self):
        """Resets the form entries"""
        pass
            
    def get_errors(self):
        """Get a list of field errors in the form"""
        errors={}
        
        """for key, widget in self.inputs.items():
            if hasattr(widget.input, 'trigger_focusout_validation'):
                widget.input.trigger_focusout_validation()
            if widget.error.get():
                errors[key] = widget.error.get()"""
            
        return errors
    
    def populate_form(self,fields):
        """ Populate Form"""
        
        self.inputs['FITS Header Value'].set(fields['fits_header_image_value'])
        self.inputs['Filename Text'].set(fields['filename_text'])
        self.inputs['Use FITS Header'].set(fields['use_fits'])
        self.inputs['Update FITS Header'].set(fields.as_bool('update_fits'))
        self.inputs['Filename Filter Text'].set(fields['filename_text_filter'])
        self.inputs['Use FITS Header Filter'].set(fields['use_fits_filter'])
        self.inputs['Update FITS Header Filter'].set(fields.as_bool('update_fits_filter'))

    def save_form(self,fields):
        """ Save Form"""

        fields['fits_header_image_value'] = self.inputs['FITS Header Value'].get()
        fields['filename_text'] = self.inputs['Filename Text'].get()
        fields['use_fits'] = self.inputs['Use FITS Header'].get()
        fields['update_fits'] = self.inputs['Update FITS Header'].get()
        fields['filename_text_filter'] = self.inputs['Filename Filter Text'].get()
        fields['use_fits_filter'] = self.inputs['Use FITS Header Filter'].get()
        fields['update_fits_filter'] = self.inputs['Update FITS Header Filter'].get()

        return fields

class MasterDetailsConfigurationForm(tk.Frame):
    """The master details configuration form"""
    
    def __init__(self, parent, fields, settings, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.settings = settings
        self.callbacks = callbacks
        
        self.current_record = None
        # A dict to keep track of input widgets
        self.inputs = {}
        
        # Styles
        style = ttk.Style()
        
        style.configure('MasterDetails.TLabel',background='lightgreen')
        style.configure('MasterDetails.TCheckbutton',background='lightgreen')
        
        # Master Details
        MasterDetails = tk.LabelFrame(self, 
                                   text="Master Details",
                                   bg="lightgreen",
                                   padx=10,
                                   pady=10
                                   )
        
        # Line 1
        self.inputs['Filename Master Bias'] = w.LabelInput(
                MasterDetails, "Filename Master Bias",
                field_spec=fields['filename_bias'],
                label_args={'style':'MasterDetails.TLabel'})
        self.inputs['Filename Master Bias'].grid(row=0, column=0)

        self.inputs['Filename Master Dark'] = w.LabelInput(
                MasterDetails, "Filename Master Dark",
                field_spec=fields['filename_dark'],
                label_args={'style':'MasterDetails.TLabel'})
        self.inputs['Filename Master Dark'].grid(row=0, column=1)

        self.inputs['Filename Master Flat'] = w.LabelInput(
                MasterDetails, "Filename Master Flat",
                field_spec=fields['filename_flat'],
                label_args={'style':'MasterDetails.TLabel'})
        self.inputs['Filename Master Flat'].grid(row=0, column=2)

        # Line 2
        self.inputs['FITS Header Image Value Bias'] = w.LabelInput(
                MasterDetails, "FITS Header Image Value Bias",
                field_spec=fields['fits_header_image_value_bias'],
                label_args={'style':'MasterDetails.TLabel'})
        self.inputs['FITS Header Image Value Bias'].grid(row=1, column=0)

        self.inputs['FITS Header Image Value Dark'] = w.LabelInput(
                MasterDetails, "FITS Header Image Value Dark",
                field_spec=fields['fits_header_image_value_dark'],
                label_args={'style':'MasterDetails.TLabel'})
        self.inputs['FITS Header Image Value Dark'].grid(row=1, column=1)

        self.inputs['FITS Header Image Value Flat'] = w.LabelInput(
                MasterDetails, "FITS Header Image Value Flat",
                field_spec=fields['fits_header_image_value_flat'],
                label_args={'style':'MasterDetails.TLabel'})
        self.inputs['FITS Header Image Value Flat'].grid(row=1, column=2)

        #Line 3
        self.inputs['Update FITS Header'] = w.LabelInput(
                MasterDetails, "Update FITS Header",
                field_spec=fields['update_fits'],
                label_args={'style':'MasterDetails.TLabel'},
                input_args={'style':'MasterDetails.TCheckbutton'})
        self.inputs['Update FITS Header'].grid(row=2, column=0, columnspan=3)
        
        MasterDetails.grid(row=0, column=0, sticky=tk.W + tk.E)
 
        self.reset()
        
    def get(self):
        data = {}
        for key, widget in self.inputs.items():
            data[key] = widget.get()
        return data
    
    def reset(self):
        """Resets the form entries"""
        pass
            
    def get_errors(self):
        """Get a list of field errors in the form"""
        errors={}
        
        """for key, widget in self.inputs.items():
            if hasattr(widget.input, 'trigger_focusout_validation'):
                widget.input.trigger_focusout_validation()
            if widget.error.get():
                errors[key] = widget.error.get()"""
            
        return errors
    
    def populate_form(self,fields):
        """ Populate Form"""
        
        self.inputs['Filename Master Bias'].set(fields['filename_bias'])
        self.inputs['Filename Master Dark'].set(fields['filename_dark'])
        self.inputs['Filename Master Flat'].set(fields['filename_flat'])
        self.inputs['FITS Header Image Value Bias'].set(fields['fits_header_image_value_bias'])
        self.inputs['FITS Header Image Value Dark'].set(fields['fits_header_image_value_dark'])
        self.inputs['FITS Header Image Value Flat'].set(fields['fits_header_image_value_flat'])
        self.inputs['Update FITS Header'].set(fields.as_bool('update_fits'))

    def save_form(self,fields):
        """ Save Form"""

        fields['filename_bias'] = self.inputs['Filename Master Bias'].get()
        fields['filename_dark'] = self.inputs['Filename Master Dark'].get()
        fields['filename_flat'] = self.inputs['Filename Master Flat'].get()
        fields['fits_header_image_value_bias'] = self.inputs['FITS Header Image Value Bias'].get()
        fields['fits_header_image_value_dark'] = self.inputs['FITS Header Image Value Dark'].get()
        fields['fits_header_image_value_flat'] = self.inputs['FITS Header Image Value Flat'].get()
        fields['update_fits'] = self.inputs['Update FITS Header'].get()

        return fields

class ReducedDetailsConfigurationForm(tk.Frame):
    """The reduced details configuration form"""
    
    def __init__(self, parent, fields, settings, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.settings = settings
        self.callbacks = callbacks
        
        self.current_record = None
        # A dict to keep track of input widgets
        self.inputs = {}
        
        # Styles
        style = ttk.Style()
        
        style.configure('ReductionDetails.TLabel',background='lightgreen')
        style.configure('ReductionDetails.TCheckbutton',background='lightgreen')
        style.configure('ReductionDetails.TRadiobutton',background='lightgreen')
        
        # Reduction Details
        ReductionDetails = tk.LabelFrame(self, 
                                   text="Reduction Details",
                                   bg="lightgreen",
                                   padx=10,
                                   pady=10
                                   )
        
        # Line 1
        self.inputs['Filename Bias Stub'] = w.LabelInput(
                ReductionDetails, "Filename Master Bias",
                field_spec=fields['filename_bias_stub'],
                label_args={'style':'ReductionDetails.TLabel'})
        self.inputs['Filename Bias Stub'].grid(row=0, column=0)

        # Line 2
        self.inputs['Filename Dark Stub'] = w.LabelInput(
                ReductionDetails, "Filename Master Dark",
                field_spec=fields['filename_dark_stub'],
                label_args={'style':'ReductionDetails.TLabel'})
        self.inputs['Filename Dark Stub'].grid(row=1, column=0)

        # Line 3
        self.inputs['Filename Flat Stub'] = w.LabelInput(
                ReductionDetails, "Filename Master Flat",
                field_spec=fields['filename_flat_stub'],
                label_args={'style':'ReductionDetails.TLabel'})
        self.inputs['Filename Flat Stub'].grid(row=2, column=0)

        # Line 4
        self.inputs['Filename Reduced Stub'] = w.LabelInput(
                ReductionDetails, "Filename Master Reduced",
                field_spec=fields['filename_reduced_stub'],
                label_args={'style':'ReductionDetails.TLabel'})
        self.inputs['Filename Reduced Stub'].grid(row=3, column=0)

        # Line 5
        self.inputs['Filename Stub Modifier'] = w.LabelInput(
                ReductionDetails, "Filename Stub Modifier",
                field_spec=fields['filename_prefix_suffix_modifier'],
                label_args={'style':'ReductionDetails.TLabel'})
        self.inputs['Filename Stub Modifier'].grid(row=4, column=0)

        # Line 6
        self.filename_stub_prefix_radiobutton = tk.StringVar()
        self.inputs['Filename Modifier Prefix'] = w.LabelInput(
                ReductionDetails, "Filename Modifier Prefix",
                input_var = self.filename_stub_prefix_radiobutton,               
                field_spec=fields['filename_stub_prefix'],
                label_args={'style':'ReductionDetails.TLabel'},
                input_args={'style':'ReductionDetails.TRadiobutton',
                                'variable':'self.filename_stub_prefix_radiobutton',
                                'value':'True'})
        self.inputs['Filename Modifier Prefix'].grid(row=5, column=0, columnspan=1)

        self.inputs['Filename Modifier Suffix'] = w.LabelInput(
                ReductionDetails, "Filename Modifier Suffix",
                input_var = self.filename_stub_prefix_radiobutton,
                field_spec=fields['filename_stub_prefix'],
                label_args={'style':'ReductionDetails.TLabel'},
                input_args={'style':'ReductionDetails.TRadiobutton',
                                'variable':'self.filename_stub_prefix_radiobutton',
                                'value':'False'})
        self.inputs['Filename Modifier Suffix'].grid(row=5, column=1, columnspan=1)

        ReductionDetails.grid(row=0, column=0, sticky=tk.W + tk.E)

        self.reset()
        
    def get(self):
        data = {}
        for key, widget in self.inputs.items():
            data[key] = widget.get()
        return data
    
    def reset(self):
        """Resets the form entries"""
        pass
            
    def get_errors(self):
        """Get a list of field errors in the form"""
        errors={}
        
        """for key, widget in self.inputs.items():
            if hasattr(widget.input, 'trigger_focusout_validation'):
                widget.input.trigger_focusout_validation()
            if widget.error.get():
                errors[key] = widget.error.get()"""
            
        return errors
    
    def populate_form(self,fields):
        """ Populate Form"""
        
        self.inputs['Filename Bias Stub'].set(fields['filename_bias_stub'])
        self.inputs['Filename Dark Stub'].set(fields['filename_dark_stub'])
        self.inputs['Filename Flat Stub'].set(fields['filename_flat_stub'])
        self.inputs['Filename Reduced Stub'].set(fields['filename_reduced_stub'])
        self.inputs['Filename Stub Modifier'].set(fields['filename_prefix_suffix_modifier'])
        self.inputs['Filename Modifier Prefix'].set(fields['filename_stub_prefix'])

    def save_form(self,fields):
        """ Save Form"""

        fields['filename_bias_stub'] = self.inputs['Filename Bias Stub'].get()
        fields['filename_dark_stub'] = self.inputs['Filename Dark Stub'].get()
        fields['filename_flat_stub'] = self.inputs['Filename Flat Stub'].get()
        fields['filename_reduced_stub'] = self.inputs['Filename Reduced Stub'].get()
        fields['filename_prefix_suffix_modifier'] = self.inputs['Filename Stub Modifier'].get()
        fields['filename_stub_prefix'] = self.inputs['Filename Modifier Prefix'].get()

        return fields








