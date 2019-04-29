import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
from astropy.visualization import astropy_mpl_style

import numpy as np

from astropy.utils.data import get_pkg_data_filename
from astropy.io import fits

from PIL import Image
from PIL import ImageTk

from . import widgets as w

from .constants import FieldTypes as FT

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

        style.configure('headerinfo.TLabel',background='grey85')

        # Build the form
        # A dict to keep track of input widgets
        self.inputs = {}

        # header section
        headerinfo = tk.LabelFrame(
            self,
            text="Header Information",
            bg="grey85",
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
        nh = ttk.Notebook(headerinfo)
        fh1 = ttk.Frame(nh) # Frame for Primary Header
        fh2 = ttk.Frame(nh) # Frame for Extension Header
        nh.add(fh1, text='Primary Header')
        nh.add(fh2, text='Extension Header')

        nh.grid(sticky="w", row=1, column=2, padx=10, pady=10)

        # Box for Primary Header
        self.inputs['P_Header'] = w.LabelInput(
            fh1, "Primary Header",
            field_spec=fields['P_Header'],
            input_args={"width": 80, "height": 50}
        )

        # scrollbar for Primary Header
        self.p_headscrollbar = tk.Scrollbar(
            fh1,
            orient=tk.VERTICAL,
            command=self.inputs['P_Header'].input.yview)

        self.inputs['P_Header'].input.config(yscrollcommand=self.p_headscrollbar.set)

        self.inputs['P_Header'].input.config(state='disabled')
        self.inputs['P_Header'].grid(sticky="w", row=0, column=0, padx=10, pady=10)
        self.p_headscrollbar.grid(row=0,column=1,sticky='NSW')


        # Box for Extension Header
        self.inputs['Ex_Header'] = w.LabelInput(
            fh2, "Extension Header",
            field_spec=fields['Ex_Header'],
            input_args={"width": 80, "height": 50}
        )

        # scrollbar for Extension Header
        self.ex_headscrollbar = tk.Scrollbar(
            fh2,
            orient=tk.VERTICAL,
            command=self.inputs['Ex_Header'].input.yview)

        self.inputs['Ex_Header'].input.config(yscrollcommand=self.ex_headscrollbar.set)

        self.inputs['Ex_Header'].input.config(state='disabled')
        self.inputs['Ex_Header'].grid(sticky="w", row=0, column=0, padx=10, pady=10)
        self.ex_headscrollbar.grid(row=0,column=1,sticky='NSW')

        # Image display
        ni = ttk.Notebook(headerinfo)
        fi1 = ttk.Frame(ni) # Frame for Primary Image
        fi2 = ttk.Frame(ni) # Frame for Extension Image
        ni.add(fi1, text='Primary Image')
        ni.add(fi2, text='Extension Image')

        ni.grid(sticky="w", row=1, column=5, padx=10, pady=10)

        # Primary Image
        self.p_canvas = tk.Canvas(
            fi1, width=512,height=512
        )
        self.p_canvasxsb = tk.Scrollbar(fi1, orient=tk.HORIZONTAL, command=self.p_canvas.xview)
        self.p_canvasysb = tk.Scrollbar(fi1, orient=tk.VERTICAL, command=self.p_canvas.yview)
        self.p_canvas.configure(yscrollcommand=self.p_canvasysb.set, xscrollcommand=self.p_canvasxsb.set)
        
        self.p_canvasxsb.grid(row=201, column=0, sticky="ews")
        self.p_canvasysb.grid(row=0, rowspan=200, column=1, sticky="nsw")

        self.p_canvas.grid(sticky=tk.N+tk.S+tk.E+tk.W, row=0, rowspan=200, column=0, padx=10, pady=10)

        # Primary Data
        self.p_datamin = tk.DoubleVar()
        self.p_datamax = tk.DoubleVar()
        self.p_datamean = tk.DoubleVar()
        self.p_datamedian = tk.DoubleVar()
        self.p_datastddev = tk.DoubleVar()

        tk.Label(fi1,text='Min:').grid(sticky=tk.E, row=50, column=3, padx=10, pady=10)
        tk.Label(fi1,text='Max:').grid(sticky=tk.E, row=51, column=3, padx=10, pady=10)
        tk.Label(fi1,text='Mean:').grid(sticky=tk.E, row=52, column=3, padx=10, pady=10)
        tk.Label(fi1,text='Median:').grid(sticky=tk.E, row=53, column=3, padx=10, pady=10)
        tk.Label(fi1,text='StdDev:').grid(sticky=tk.E, row=54, column=3, padx=10, pady=10)

        minval = tk.Label(fi1,textvariable=self.p_datamin)
        minval.grid(row=50, column=4, padx=10, pady=10)

        maxval = tk.Label(fi1,textvariable=self.p_datamax)
        maxval.grid(row=51, column=4, padx=10, pady=10)

        medianval = tk.Label(fi1,textvariable=self.p_datamedian)
        medianval.grid(row=52, column=4, padx=10, pady=10)

        meanval = tk.Label(fi1,textvariable=self.p_datamean)
        meanval.grid(row=53, column=4, padx=10, pady=10)

        stddevval = tk.Label(fi1,textvariable=self.p_datastddev)
        stddevval.grid(row=54, column=4, padx=10, pady=10)
        
        # Extension Image
        self.ex_canvas = tk.Canvas(
            fi2, width=512,height=512
        )
        self.ex_canvasxsb = tk.Scrollbar(fi2, orient=tk.HORIZONTAL, command=self.ex_canvas.xview)
        self.ex_canvasysb = tk.Scrollbar(fi2, orient=tk.VERTICAL, command=self.ex_canvas.yview)
        self.ex_canvas.configure(yscrollcommand=self.ex_canvasysb.set, xscrollcommand=self.ex_canvasxsb.set)
        
        self.ex_canvasxsb.grid(row=201, column=0, sticky="ews")
        self.ex_canvasysb.grid(row=0, rowspan=200, column=1, sticky="nsw")

        self.ex_canvas.grid(sticky=tk.N+tk.S+tk.E+tk.W, row=0, rowspan=200, column=0, padx=10, pady=10)

        # Extension Data
        self.ex_datamin = tk.DoubleVar()
        self.ex_datamax = tk.DoubleVar()
        self.ex_datamean = tk.DoubleVar()
        self.ex_datamedian = tk.DoubleVar()
        self.ex_datastddev = tk.DoubleVar()

        tk.Label(fi2,text='Min:').grid(sticky=tk.E, row=50, column=3, padx=10, pady=10)
        tk.Label(fi2,text='Max:').grid(sticky=tk.E, row=51, column=3, padx=10, pady=10)
        tk.Label(fi2,text='Mean:').grid(sticky=tk.E, row=52, column=3, padx=10, pady=10)
        tk.Label(fi2,text='Median:').grid(sticky=tk.E, row=53, column=3, padx=10, pady=10)
        tk.Label(fi2,text='StdDev:').grid(sticky=tk.E, row=54, column=3, padx=10, pady=10)

        minval = tk.Label(fi2,textvariable=self.ex_datamin)
        minval.grid(row=50, column=4, padx=10, pady=10)

        maxval = tk.Label(fi2,textvariable=self.ex_datamax)
        maxval.grid(row=51, column=4, padx=10, pady=10)

        medianval = tk.Label(fi2,textvariable=self.ex_datamedian)
        medianval.grid(row=52, column=4, padx=10, pady=10)

        meanval = tk.Label(fi2,textvariable=self.ex_datamean)
        meanval.grid(row=53, column=4, padx=10, pady=10)

        stddevval = tk.Label(fi2,textvariable=self.ex_datastddev)
        stddevval.grid(row=54, column=4, padx=10, pady=10)

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

    def load_p_header(self,header,*args):

        self.inputs['P_Header'].input.config(state='normal')
        self.inputs['P_Header'].set(header)
        self.inputs['P_Header'].input.config(state='disabled')

    def load_ex_header(self,header,*args):

        self.inputs['Ex_Header'].input.config(state='normal')
        self.inputs['Ex_Header'].set(header)
        self.inputs['Ex_Header'].input.config(state='disabled')

    def load_p_image(self,image = None,*args):

        if image is None:
            return[]

        width = self.p_canvas.winfo_reqwidth()       
        height = self.p_canvas.winfo_reqheight()  
        
        plt.imsave("temppimgfile.png", image, cmap=plt.cm.gray)

        img = Image.open("temppimgfile.png")
        img = img.resize((width,height), Image.ANTIALIAS)

        photo = ImageTk.PhotoImage(img)
        
        self.p_canvas.photolist = []

        self.p_canvas.create_image(0,0,image=photo,anchor="nw")
        self.p_canvas.configure(scrollregion=(0,0,width,height))
        
        self.p_canvas.photolist.append(photo)

        self.p_datamin.set(format(np.min(image),'.2f'))
        self.p_datamax.set(format(np.max(image),'.2f'))
        self.p_datamean.set(format(np.mean(image),'.2f'))
        self.p_datamedian.set(format(np.median(image),'.2f'))
        self.p_datastddev.set(format(np.std(image),'.2f'))

    def load_ex_image(self,image = None,*args):

        if image is None or image[0] is None:
            self.ex_canvas.photolist = []

            self.ex_datamin.set(format(0,'.2f'))
            self.ex_datamax.set(format(0,'.2f'))
            self.ex_datamean.set(format(0,'.2f'))
            self.ex_datamedian.set(format(0,'.2f'))
            self.ex_datastddev.set(format(0,'.2f'))

            return[]

        width = self.ex_canvas.winfo_reqwidth()       
        height = self.ex_canvas.winfo_reqheight() 

        plt.imsave("tempeximgfile.png", image, cmap=plt.cm.gray)

        img = Image.open("tempeximgfile.png")
        img = img.resize((width,height), Image.ANTIALIAS)

        photo = ImageTk.PhotoImage(img)
        
        self.ex_canvas.photolist = []

        self.ex_canvas.create_image(0,0,image=photo,anchor="nw")
        self.ex_canvas.configure(scrollregion=(0,0,width,height))
        
        self.ex_canvas.photolist.append(photo)     

        self.ex_datamin.set(format(np.min(image),'.2f'))
        self.ex_datamax.set(format(np.max(image),'.2f'))
        self.ex_datamean.set(format(np.mean(image),'.2f'))
        self.ex_datamedian.set(format(np.median(image),'.2f'))
        self.ex_datastddev.set(format(np.std(image),'.2f'))

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

        self.settings = settings
        self.callbacks = callbacks

        # Styles
        style = ttk.Style()

        style.configure('sourceselframe.TLabel',background='grey85')
        style.configure('sourceselframe.TRadiobutton',background='grey85')
        style.configure('redstepsframe.TLabel',background='grey85')
        style.configure('redstepsframe.TRadiobutton',background='grey85')
        style.configure('statusframe.TLabel',background='grey85')

        # Build the form
        # A dict to keep track of input widgets
        self.inputs = {}
        self.steps = {}

        # Source Selection
        sourceselframe = tk.LabelFrame(self, 
                                   text="Source Selection",
                                   bg="grey85",
                                   padx=10,
                                   pady=10
                                   )
        
        #Line 1
        self.steps['single'] = tk.StringVar()
        self.steps['single'].set('True')
        self.inputs['Single Directory'] = w.LabelInput(
                sourceselframe, "Single Directory",
                input_var=self.steps['single'], 
                field_spec={'req': False,'type':FT.rstring,'value':'True'},
                label_args={'style':'SourceSel.TLabel'},
                input_args={'style':'SourceSel.TRadiobutton',
                                'variable':"self.steps['single']",
                                'value' : 'True'})
        self.inputs['Single Directory'].grid(row=1, column=0, columnspan=1)

        self.inputs['Multiple Directories'] = w.LabelInput(
                sourceselframe, "Multiple Directories",
                input_var=self.steps['single'], 
                field_spec={'req': False,'type':FT.rstring,'value':'True'},
                label_args={'style':'SourceSel.TLabel'},
                input_args={'style':'SourceSel.TRadiobutton',
                                'variable':"self.steps['single']",
                                'value' : 'False'})
        self.inputs['Multiple Directories'].grid(row=1, column=1, columnspan=1)

        sourceselframe.grid(row=0, column=0, sticky=tk.W + tk.E)

        # Reduction Steps
        redstepsframe = tk.LabelFrame(self, 
                                   text="Reduction Steps",
                                   bg="grey85",
                                   padx=10,
                                   pady=10
                                   )
        
        #Line 1
        self.steps['CreateDir'] = tk.StringVar()
        self.steps['CreateDir'].set('True')
        self.inputs['Create Directories Y'] = w.LabelInput(
                redstepsframe, "Y",
                input_var=self.steps['CreateDir'], 
                field_spec={'req': False,'type':FT.rstring,'value':'True'},
                label_args={'style':'RedSteps.TLabel'},
                input_args={'style':'RedSteps.TRadiobutton',
                                'variable':"self.steps['CreateDir']",
                                'value' : 'True'})
        self.inputs['Create Directories Y'].grid(row=1, column=0, columnspan=1)

        self.inputs['Create Directories N'] = w.LabelInput(
                redstepsframe, "N: Create Directories",
                input_var=self.steps['CreateDir'], 
                field_spec={'req': False,'type':FT.rstring,'value':'True'},
                label_args={'style':'RedSteps.TLabel'},
                input_args={'style':'RedSteps.TRadiobutton',
                                'variable':"self.steps['CreateDir']",
                                'value' : 'False'})
        self.inputs['Create Directories N'].grid(row=1, column=1, columnspan=1)

        #Line 2
        self.steps['CopyImages'] = tk.StringVar()
        self.steps['CopyImages'].set('True')
        self.inputs['Copy Images Y'] = w.LabelInput(
                redstepsframe, "Y",
                input_var=self.steps['CopyImages'], 
                field_spec={'req': False,'type':FT.rstring,'value':'True'},
                label_args={'style':'RedSteps.TLabel'},
                input_args={'style':'RedSteps.TRadiobutton',
                                'variable':"self.steps['CopyImages'] Images",
                                'value' : 'True'})
        self.inputs['Copy Images Y'].grid(row=2, column=0, columnspan=1)

        self.inputs['Copy Images N'] = w.LabelInput(
                redstepsframe, "N: Copy Images",
                input_var=self.steps['CopyImages'], 
                field_spec={'req': False,'type':FT.rstring,'value':'True'},
                label_args={'style':'RedSteps.TLabel'},
                input_args={'style':'RedSteps.TRadiobutton',
                                'variable':"self.steps['CopyImages']",
                                'value' : 'False'})
        self.inputs['Copy Images N'].grid(row=2, column=1, columnspan=1)

        #Line 3
        self.steps['CreateMasters'] = tk.StringVar()
        self.steps['CreateMasters'].set('True')
        self.inputs['Create Masters Y'] = w.LabelInput(
                redstepsframe, "Y",
                input_var=self.steps['CreateMasters'], 
                field_spec={'req': False,'type':FT.rstring,'value':'True'},
                label_args={'style':'RedSteps.TLabel'},
                input_args={'style':'RedSteps.TRadiobutton',
                                'variable':"self.steps['CreateMasters']",
                                'value' : 'True'})
        self.inputs['Create Masters Y'].grid(row=3, column=0, columnspan=1)

        self.inputs['Create Masters N'] = w.LabelInput(
                redstepsframe, "N: Create Masters",
                input_var=self.steps['CreateMasters'], 
                field_spec={'req': False,'type':FT.rstring,'value':'True'},
                label_args={'style':'RedSteps.TLabel'},
                input_args={'style':'RedSteps.TRadiobutton',
                                'variable':"self.steps['CreateMasters']",
                                'value' : 'False'})
        self.inputs['Create Masters N'].grid(row=3, column=1, columnspan=1)

        #Line 4
        self.steps['BiasRemoval'] = tk.StringVar()
        self.steps['BiasRemoval'].set('True')
        self.inputs['Bias Removal Y'] = w.LabelInput(
                redstepsframe, "Y",
                input_var=self.steps['BiasRemoval'], 
                field_spec={'req': False,'type':FT.rstring,'value':'True'},
                label_args={'style':'RedSteps.TLabel'},
                input_args={'style':'RedSteps.TRadiobutton',
                                'variable':"self.steps['BiasRemoval']",
                                'value' : 'True'})
        self.inputs['Bias Removal Y'].grid(row=4, column=0, columnspan=1)

        self.inputs['Bias Removal N'] = w.LabelInput(
                redstepsframe, "N: Bias Removal",
                input_var=self.steps['BiasRemoval'], 
                field_spec={'req': False,'type':FT.rstring,'value':'True'},
                label_args={'style':'RedSteps.TLabel'},
                input_args={'style':'RedSteps.TRadiobutton',
                                'variable':"self.steps['BiasRemoval']",
                                'value' : 'False'})
        self.inputs['Bias Removal N'].grid(row=4, column=1, columnspan=1)

        #Line 5
        self.steps['DarkRemoval'] = tk.StringVar()
        self.steps['DarkRemoval'].set('True')
        self.inputs['Dark Removal Y'] = w.LabelInput(
                redstepsframe, "Y",
                input_var=self.steps['DarkRemoval'], 
                field_spec={'req': False,'type':FT.rstring,'value':'True'},
                label_args={'style':'RedSteps.TLabel'},
                input_args={'style':'RedSteps.TRadiobutton',
                                'variable':"self.steps['DarkRemoval']",
                                'value' : 'True'})
        self.inputs['Dark Removal Y'].grid(row=5, column=0, columnspan=1)

        self.inputs['Dark Removal N'] = w.LabelInput(
                redstepsframe, "N: Dark Removal",
                input_var=self.steps['DarkRemoval'], 
                field_spec={'req': False,'type':FT.rstring,'value':'True'},
                label_args={'style':'RedSteps.TLabel'},
                input_args={'style':'RedSteps.TRadiobutton',
                                'variable':"self.steps['DarkRemoval']",
                                'value' : 'False'})
        self.inputs['Dark Removal N'].grid(row=5, column=1, columnspan=1)

        #Line 6
        self.steps['PerformReduction'] = tk.StringVar()
        self.steps['PerformReduction'].set('True')
        self.inputs['Perform Reduction Y'] = w.LabelInput(
                redstepsframe, "Y",
                input_var=self.steps['PerformReduction'], 
                field_spec={'req': False,'type':FT.rstring,'value':'True'},
                label_args={'style':'RedSteps.TLabel'},
                input_args={'style':'RedSteps.TRadiobutton',
                                'variable':"self.steps['PerformReduction']",
                                'value' : 'True'})
        self.inputs['Perform Reduction Y'].grid(row=6, column=0, columnspan=1)

        self.inputs['Perform Reduction N'] = w.LabelInput(
                redstepsframe, "N: Perform Reduction",
                input_var=self.steps['PerformReduction'], 
                field_spec={'req': False,'type':FT.rstring,'value':'True'},
                label_args={'style':'RedSteps.TLabel'},
                input_args={'style':'RedSteps.TRadiobutton',
                                'variable':"self.steps['PerformReduction']",
                                'value' : 'False'})
        self.inputs['Perform Reduction N'].grid(row=6, column=1, columnspan=1)

        #Line 7
        self.steps['CopyResults'] = tk.StringVar()
        self.steps['CopyResults'].set('True')
        self.inputs['Copy Results Y'] = w.LabelInput(
                redstepsframe, "Y",
                input_var=self.steps['CopyResults'], 
                field_spec={'req': False,'type':FT.rstring,'value':'True'},
                label_args={'style':'RedSteps.TLabel'},
                input_args={'style':'RedSteps.TRadiobutton',
                                'variable':"self.steps['CopyResults']",
                                'value' : 'True'})
        self.inputs['Copy Results Y'].grid(row=7, column=0, columnspan=1)

        self.inputs['Copy Results N'] = w.LabelInput(
                redstepsframe, "N: Copy Results",
                input_var=self.steps['CopyResults'], 
                field_spec={'req': False,'type':FT.rstring,'value':'True'},
                label_args={'style':'RedSteps.TLabel'},
                input_args={'style':'RedSteps.TRadiobutton',
                                'variable':"self.steps['CopyResults']",
                                'value' : 'False'})
        self.inputs['Copy Results N'].grid(row=7, column=1, columnspan=1)

        #Line 8
        self.steps['CopyWorking'] = tk.StringVar()
        self.steps['CopyWorking'].set('True')
        self.inputs['Copy Working Y'] = w.LabelInput(
                redstepsframe, "Y",
                input_var=self.steps['CopyWorking'], 
                field_spec={'req': False,'type':FT.rstring,'value':'True'},
                label_args={'style':'RedSteps.TLabel'},
                input_args={'style':'RedSteps.TRadiobutton',
                                'variable':"self.steps['CopyWorking']",
                                'value' : 'True'})
        self.inputs['Copy Working Y'].grid(row=8, column=0, columnspan=1)

        self.inputs['Copy Working N'] = w.LabelInput(
                redstepsframe, "N: Copy Working",
                input_var=self.steps['CopyWorking'], 
                field_spec={'req': False,'type':FT.rstring,'value':'True'},
                label_args={'style':'RedSteps.TLabel'},
                input_args={'style':'RedSteps.TRadiobutton',
                                'variable':"self.steps['CopyWorking']",
                                'value' : 'False'})
        self.inputs['Copy Working N'].grid(row=8, column=1, columnspan=1)

        #Line 9
        self.steps['DeleteDir'] = tk.StringVar()
        self.steps['DeleteDir'].set('True')
        self.inputs['Delete Directories Y'] = w.LabelInput(
                redstepsframe, "Y",
                input_var=self.steps['DeleteDir'], 
                field_spec={'req': False,'type':FT.rstring,'value':'True'},
                label_args={'style':'RedSteps.TLabel'},
                input_args={'style':'RedSteps.TRadiobutton',
                                'variable':"self.steps['DeleteDir']",
                                'value' : 'True'})
        self.inputs['Delete Directories Y'].grid(row=9, column=0, columnspan=1)

        self.inputs['Delete Directories N'] = w.LabelInput(
                redstepsframe, "N: Delete Directories",
                input_var=self.steps['DeleteDir'], 
                field_spec={'req': False,'type':FT.rstring,'value':'True'},
                label_args={'style':'RedSteps.TLabel'},
                input_args={'style':'RedSteps.TRadiobutton',
                                'variable':"self.steps['DeleteDir']",
                                'value' : 'False'})
        self.inputs['Delete Directories N'].grid(row=9, column=1, columnspan=1)

        #Line 10
        self.RedButton = tk.Button(redstepsframe, 
                text='Perform Reduction',
                command=self.callbacks['reduction->go'],)
        self.RedButton.grid(row=10, column=0, columnspan=2)

        redstepsframe.grid(row=1, column=0, sticky=tk.W + tk.E)

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
        
        style.configure('Directories.TLabel',background='grey85')
        style.configure('Directories.TCheckbutton',background='grey85')
        
        # Directories
        Directories = tk.LabelFrame(self, 
                                   text="Directories",
                                   bg="grey85",
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
        
        style.configure('GeneralDetails.TLabel',background='grey85')
        style.configure('GeneralDetails.TCheckbutton',background='grey85')
         
        # General Details
        GeneralDetails = tk.LabelFrame(self, 
                                   text="General Details",
                                   bg="grey85",
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

        # Line 3
        self.inputs['CCD Gain'] = w.LabelInput(
                GeneralDetails, "CCD Gain",
                field_spec=fields['ccd_gain'],
                label_args={'style':'GeneralDetails.TLabel'})
        self.inputs['CCD Gain'].grid(row=2, column=0)

        self.inputs['CCD Readnoise'] = w.LabelInput(
                GeneralDetails, "CCD Readnoise",
                field_spec=fields['ccd_readnoise'],
                label_args={'style':'GeneralDetails.TLabel'})
        self.inputs['CCD Readnoise'].grid(row=2, column=1)

        # Line 4
        self.inputs['File Use'] = w.LabelInput(
                GeneralDetails, "File Use",
                field_spec=fields['file_usage'],
                label_args={'style':'GeneralDetails.TLabel'})
        self.inputs['File Use'].grid(row=3, column=0)

        self.inputs['External Directory'] = w.LabelInput(
                GeneralDetails, "External Directory",
                field_spec=fields['ext_directory'],
                label_args={'style':'GeneralDetails.TLabel'})
        self.inputs['External Directory'].grid(row=3, column=1)

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
        
        return errors
    
    def populate_form(self,fields):
        """ Populate Form"""
        
        self.inputs['FITS Header Image Type'].set(fields['fits_header_image_type'])
        self.inputs['FITS Header Filter'].set(fields['fits_header_filter'])
        self.inputs['FITS Header Exposure'].set(fields['fits_header_exposure'])
        self.inputs['FITS Header CCD Temp'].set(fields['fits_header_CCD_temp'])
        self.inputs['CCD Gain'].set(fields['ccd_gain'])
        self.inputs['CCD Readnoise'].set(fields['ccd_readnoise'])
        self.inputs['File Use'].set(fields['file_usage'])
        self.inputs['External Directory'].set(fields['ext_directory'])

    def save_form(self,fields):
        """ Save Form"""

        fields['fits_header_image_type'] = self.inputs['FITS Header Image Type'].get()
        fields['fits_header_filter'] = self.inputs['FITS Header Filter'].get()
        fields['fits_header_exposure'] = self.inputs['FITS Header Exposure'].get()
        fields['fits_header_CCD_temp'] = self.inputs['FITS Header CCD Temp'].get()
        fields['ccd_gain'] = self.inputs['CCD Gain'].get()
        fields['ccd_readnoise'] = self.inputs['CCD Readnoise'].get()
        fields['file_usage'] = self.inputs['File Use'].get()
        fields['ext_directory'] = self.inputs['External Directory'].get()

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
        
        style.configure('BiasDetails.TLabel',background='grey85')
        style.configure('BiasDetails.TCheckbutton',background='grey85')
        style.configure('BiasDetails.TRadiobutton',background='grey85')
        
        # Bias Details
        BiasDetails = tk.LabelFrame(self, 
                                   text="Bias Details",
                                   bg="grey85",
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
        self.inputs['Update FITS Header'].grid(row=2, column=0, columnspan=1)

        #Line 4
        self.inputs['Median Filter'] = w.LabelInput(
                BiasDetails, "Perform Median Filter",
                field_spec=fields['perform_median_filter'],
                label_args={'style':'BiasDetails.TLabel'},
                input_args={'style':'BiasDetails.TCheckbutton'})
        self.inputs['Median Filter'].grid(row=3, column=0, columnspan=1)

        self.inputs['Median Filter Size'] = w.LabelInput(
                BiasDetails, "Filter Size",
                field_spec=fields['median_filter_size'],
                label_args={'style':'BiasDetails.TLabel'})
        self.inputs['Median Filter Size'].grid(row=3, column=1)

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
            
        return errors
    
    def populate_form(self,fields):
        """ Populate Form"""
        
        self.inputs['FITS Header Value'].set(fields['fits_header_image_value'])
        self.inputs['Filename Text'].set(fields['filename_text'])
        self.inputs['Use FITS Header'].set(fields['use_fits'])
        self.inputs['Update FITS Header'].set(fields.as_bool('update_fits'))
        self.inputs['Median Filter'].set(fields.as_bool('perform_median_filter'))
        self.inputs['Median Filter Size'].set(fields['median_filter_size'])

    def save_form(self,fields):
        """ Save Form"""

        fields['fits_header_image_value'] = self.inputs['FITS Header Value'].get()
        fields['filename_text'] = self.inputs['Filename Text'].get()
        fields['use_fits'] = self.inputs['Use FITS Header'].get()
        fields['update_fits'] = self.inputs['Update FITS Header'].get()
        fields['perform_median_filter'] = self.inputs['Median Filter'].get()
        fields['median_filter_size'] = self.inputs['Median Filter Size'].get()

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
        
        style.configure('DarkDetails.TLabel',background='grey85')
        style.configure('DarkDetails.TCheckbutton',background='grey85')
        style.configure('DarkDetails.TRadiobutton',background='grey85')
        
        # Dark Details
        DarkDetails = tk.LabelFrame(self, 
                                   text="Dark Details",
                                   bg="grey85",
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

        #Line 4
        self.inputs['Median Filter'] = w.LabelInput(
                DarkDetails, "Perform Median Filter",
                field_spec=fields['perform_median_filter'],
                label_args={'style':'DarkDetails.TLabel'},
                input_args={'style':'DarkDetails.TCheckbutton'})
        self.inputs['Median Filter'].grid(row=3, column=0, columnspan=1)

        self.inputs['Median Filter Size'] = w.LabelInput(
                DarkDetails, "Filter Size",
                field_spec=fields['median_filter_size'],
                label_args={'style':'DarkDetails.TLabel'})
        self.inputs['Median Filter Size'].grid(row=3, column=1)

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
            
        return errors
    
    def populate_form(self,fields):
        """ Populate Form"""
        
        self.inputs['FITS Header Value'].set(fields['fits_header_image_value'])
        self.inputs['Filename Text'].set(fields['filename_text'])
        self.inputs['Use FITS Header'].set(fields['use_fits'])
        self.inputs['Update FITS Header'].set(fields.as_bool('update_fits'))
        self.inputs['Median Filter'].set(fields.as_bool('perform_median_filter'))
        self.inputs['Median Filter Size'].set(fields['median_filter_size'])

    def save_form(self,fields):
        """ Save Form"""

        fields['fits_header_image_value'] = self.inputs['FITS Header Value'].get()
        fields['filename_text'] = self.inputs['Filename Text'].get()
        fields['use_fits'] = self.inputs['Use FITS Header'].get()
        fields['update_fits'] = self.inputs['Update FITS Header'].get()
        fields['perform_median_filter'] = self.inputs['Median Filter'].get()
        fields['median_filter_size'] = self.inputs['Median Filter Size'].get()

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
        
        style.configure('FlatDetails.TLabel',background='grey85')
        style.configure('FlatDetails.TCheckbutton',background='grey85')
        style.configure('FlatDetails.TRadiobutton',background='grey85')
        
        # Flat Details
        FlatDetails = tk.LabelFrame(self, 
                                   text="Flat Details",
                                   bg="grey85",
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
        self.inputs['Update FITS Header'].grid(row=2, column=0, columnspan=1)

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
        self.inputs['Update FITS Header Filter'].grid(row=5, column=0, columnspan=1)

        #Line 7
        self.inputs['Median Filter'] = w.LabelInput(
                FlatDetails, "Perform Median Filter",
                field_spec=fields['perform_median_filter'],
                label_args={'style':'FlatDetails.TLabel'},
                input_args={'style':'FlatDetails.TCheckbutton'})
        self.inputs['Median Filter'].grid(row=6, column=0, columnspan=1)

        self.inputs['Median Filter Size'] = w.LabelInput(
                FlatDetails, "Filter Size",
                field_spec=fields['median_filter_size'],
                label_args={'style':'FlatDetails.TLabel'})
        self.inputs['Median Filter Size'].grid(row=6, column=1)

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
        self.inputs['Median Filter'].set(fields.as_bool('perform_median_filter'))
        self.inputs['Median Filter Size'].set(fields['median_filter_size'])

    def save_form(self,fields):
        """ Save Form"""

        fields['fits_header_image_value'] = self.inputs['FITS Header Value'].get()
        fields['filename_text'] = self.inputs['Filename Text'].get()
        fields['use_fits'] = self.inputs['Use FITS Header'].get()
        fields['update_fits'] = self.inputs['Update FITS Header'].get()
        fields['filename_text_filter'] = self.inputs['Filename Filter Text'].get()
        fields['use_fits_filter'] = self.inputs['Use FITS Header Filter'].get()
        fields['update_fits_filter'] = self.inputs['Update FITS Header Filter'].get()
        fields['perform_median_filter'] = self.inputs['Median Filter'].get()
        fields['median_filter_size'] = self.inputs['Median Filter Size'].get()

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
        
        style.configure('ScienceDetails.TLabel',background='grey85')
        style.configure('ScienceDetails.TCheckbutton',background='grey85')
        style.configure('ScienceDetails.TRadiobutton',background='grey85')
        
        # Science Details
        ScienceDetails = tk.LabelFrame(self, 
                                   text="Science Details",
                                   bg="grey85",
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
        self.inputs['Update FITS Header'].grid(row=2, column=0, columnspan=1)

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
        self.inputs['Update FITS Header Filter'].grid(row=5, column=0, columnspan=1)

        #Line 7
        self.inputs['Median Filter'] = w.LabelInput(
                ScienceDetails, "Perform Median Filter",
                field_spec=fields['perform_median_filter'],
                label_args={'style':'ScienceDetails.TLabel'},
                input_args={'style':'ScienceDetails.TCheckbutton'})
        self.inputs['Median Filter'].grid(row=6, column=0, columnspan=1)

        self.inputs['Median Filter Size'] = w.LabelInput(
                ScienceDetails, "Filter Size",
                field_spec=fields['median_filter_size'],
                label_args={'style':'ScienceDetails.TLabel'})
        self.inputs['Median Filter Size'].grid(row=6, column=1)

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
        self.inputs['Median Filter'].set(fields.as_bool('perform_median_filter'))
        self.inputs['Median Filter Size'].set(fields['median_filter_size'])

    def save_form(self,fields):
        """ Save Form"""

        fields['fits_header_image_value'] = self.inputs['FITS Header Value'].get()
        fields['filename_text'] = self.inputs['Filename Text'].get()
        fields['use_fits'] = self.inputs['Use FITS Header'].get()
        fields['update_fits'] = self.inputs['Update FITS Header'].get()
        fields['filename_text_filter'] = self.inputs['Filename Filter Text'].get()
        fields['use_fits_filter'] = self.inputs['Use FITS Header Filter'].get()
        fields['update_fits_filter'] = self.inputs['Update FITS Header Filter'].get()
        fields['perform_median_filter'] = self.inputs['Median Filter'].get()
        fields['median_filter_size'] = self.inputs['Median Filter Size'].get()

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
        
        style.configure('MasterDetails.TLabel',background='grey85')
        style.configure('MasterDetails.TCheckbutton',background='grey85')
        
        # Master Details
        MasterDetails = tk.LabelFrame(self, 
                                   text="Master Details",
                                   bg="grey85",
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

        # Line 3
        self.inputs['Median Combine Bias'] = w.LabelInput(
                MasterDetails, "Median Combine Bias",
                field_spec=fields['median_combine_bias'],
                label_args={'style':'MasterDetails.TLabel'},
                input_args={'style':'MasterDetails.TCheckbutton'})
        self.inputs['Median Combine Bias'].grid(row=2, column=0)

        self.inputs['Median Combine Dark'] = w.LabelInput(
                MasterDetails, "Median Combine dark",
                field_spec=fields['median_combine_dark'],
                label_args={'style':'MasterDetails.TLabel'},
                input_args={'style':'MasterDetails.TCheckbutton'})
        self.inputs['Median Combine Dark'].grid(row=2, column=1)

        self.inputs['Median Combine Flat'] = w.LabelInput(
                MasterDetails, "Median Combine Flat",
                field_spec=fields['median_combine_flat'],
                label_args={'style':'MasterDetails.TLabel'},
                input_args={'style':'MasterDetails.TCheckbutton'})
        self.inputs['Median Combine Flat'].grid(row=2, column=2)

        # Line 4
        self.inputs['Update FITS Header'] = w.LabelInput(
                MasterDetails, "Update FITS Header",
                field_spec=fields['update_fits'],
                label_args={'style':'MasterDetails.TLabel'},
                input_args={'style':'MasterDetails.TCheckbutton'})
        self.inputs['Update FITS Header'].grid(row=3, column=0, columnspan=1)
        
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
            
        return errors
    
    def populate_form(self,fields):
        """ Populate Form"""
        
        self.inputs['Filename Master Bias'].set(fields['filename_bias'])
        self.inputs['Filename Master Dark'].set(fields['filename_dark'])
        self.inputs['Filename Master Flat'].set(fields['filename_flat'])
        self.inputs['FITS Header Image Value Bias'].set(fields['fits_header_image_value_bias'])
        self.inputs['FITS Header Image Value Dark'].set(fields['fits_header_image_value_dark'])
        self.inputs['FITS Header Image Value Flat'].set(fields['fits_header_image_value_flat'])
        self.inputs['Median Combine Bias'].set(fields.as_bool('median_combine_bias'))
        self.inputs['Median Combine Dark'].set(fields.as_bool('median_combine_dark'))
        self.inputs['Median Combine Flat'].set(fields.as_bool('median_combine_flat'))
        self.inputs['Update FITS Header'].set(fields.as_bool('update_fits'))

    def save_form(self,fields):
        """ Save Form"""

        fields['filename_bias'] = self.inputs['Filename Master Bias'].get()
        fields['filename_dark'] = self.inputs['Filename Master Dark'].get()
        fields['filename_flat'] = self.inputs['Filename Master Flat'].get()
        fields['fits_header_image_value_bias'] = self.inputs['FITS Header Image Value Bias'].get()
        fields['fits_header_image_value_dark'] = self.inputs['FITS Header Image Value Dark'].get()
        fields['fits_header_image_value_flat'] = self.inputs['FITS Header Image Value Flat'].get()
        fields['median_combine_bias'] = self.inputs['Median Combine Bias'].get()
        fields['median_combine_dark'] = self.inputs['Median Combine Dark'].get()
        fields['median_combine_flat'] = self.inputs['Median Combine Flat'].get()
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
        
        style.configure('ReductionDetails.TLabel',background='grey85')
        style.configure('ReductionDetails.TCheckbutton',background='grey85')
        style.configure('ReductionDetails.TRadiobutton',background='grey85')
        
        # Reduction Details
        ReductionDetails = tk.LabelFrame(self, 
                                   text="Reduction Details",
                                   bg="grey85",
                                   padx=10,
                                   pady=10
                                   )
        
        # Line 1
        self.inputs['Filename Bias Stub'] = w.LabelInput(
                ReductionDetails, "Filename Bias Subtracted",
                field_spec=fields['filename_bias_stub'],
                label_args={'style':'ReductionDetails.TLabel'})
        self.inputs['Filename Bias Stub'].grid(row=0, column=0)

        # Line 2
        self.inputs['Filename Dark Stub'] = w.LabelInput(
                ReductionDetails, "Filename Dark Removed",
                field_spec=fields['filename_dark_stub'],
                label_args={'style':'ReductionDetails.TLabel'})
        self.inputs['Filename Dark Stub'].grid(row=1, column=0)

        # Line 3
        self.inputs['Filename Flat Stub'] = w.LabelInput(
                ReductionDetails, "Filename Flat Removed",
                field_spec=fields['filename_flat_stub'],
                label_args={'style':'ReductionDetails.TLabel'})
        self.inputs['Filename Flat Stub'].grid(row=2, column=0)

        # Line 4
        self.inputs['Filename Reduced Stub'] = w.LabelInput(
                ReductionDetails, "Filename Reduced",
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








