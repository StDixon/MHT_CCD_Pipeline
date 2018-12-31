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

        # file selection treeview
        self.treeview = ttk.Treeview(
            self,
            columns=list(self.column_defs.keys())[1:],
            selectmode='browse'
        )

        # scrollbar for treeview
        self.scrollbar = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self.treeview.yview
        )
        self.treeview.configure(yscrollcommand=self.scrollbar.set)
        self.treeview.configure(show='headings')
        self.treeview.grid(row=0,column=0,sticky='NSEW')
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

        # Bind double-clicks
        self.treeview.bind('<<TreeviewOpen>>',self.on_open_image_file)

        # header display
        self.inputs['Header'] = w.LabelInput(
            self, "Header",
            field_spec=fields['Header'],
            input_args={"width": 80, "height": 50}
        )
        self.inputs['Header'].input.config(state='disabled')
        self.inputs['Header'].grid(sticky="w", row=0, column=2, padx=10, pady=10)

        # Image display
        self.canvas = tk.Canvas(
            self, width=800,height=500
            #"Image",
            #field_spec=fields['Image'],
            #input_args={"width": 80, "height": 50}
        )
        #self.inputs['Image'].input.config(state='disabled')
        #self.canvas.create_rectangle(0,0,600,400,fill='blue')
        self.canvas.grid(sticky="w", row=0, column=3, padx=10, pady=10)

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

