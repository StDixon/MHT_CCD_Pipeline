import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
from astropy.visualization import astropy_mpl_style

from astropy.utils.data import get_pkg_data_filename
from astropy.io import fits

from . import widgets as w

class ShowHeaderForm(tk.Frame):
    """Display FIT file headers"""
    
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
        self.treeview.bind('<<TreeviewOpen>>',self.on_open_file_header)

        # header display
        self.inputs['Header'] = w.LabelInput(
            self, "Header",
            field_spec=fields['Header'],
            input_args={"width": 80, "height": 50}
        )
        self.inputs['Header'].input.config(state='disabled')
        self.inputs['Header'].grid(sticky="w", row=0, column=2, padx=10, pady=10)

        headerinfo.grid(row=0,column=0,sticky="we")

        # image section
        imageinfo = tk.LabelFrame(
            self,
            text="Image Information",
            bg="lightblue",
            padx=10,
            pady=10
        )

        # Image display
        self.inputs['Image'] = w.LabelInput(
            self, "Image",
            field_spec=fields['Image'],
            input_args={"width": 80, "height": 50}
        )
        self.inputs['Image'].input.config(state='disabled')
        self.inputs['Image'].grid(sticky="w", row=0, column=3, padx=10, pady=10)

        imageinfo.grid(row=0,column=0,sticky="we")

    def populate_header(self,rows):
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

    def on_open_file_header(self,*args):

        selected_id = self.treeview.selection()[0]
        self.callbacks['on_open_file_header'](selected_id)

    def load_header(self,header,*args):

        self.inputs['Header'].input.config(state='normal')
        self.inputs['Header'].set(header)
        self.inputs['Header'].input.config(state='disabled')

    def load_image(self,image,*args):

        self.inputs['Image'].input.config(state='normal')
        self.inputs['Image'].set(image)
        self.inputs['Image'].input.config(state='disabled')

        plt.style.use(astropy_mpl_style)
        print(image.shape)
        plt.figure()
        plt.imshow(image,cmap='gray')
        plt.colorbar


    def sort(self,treeview,col):
        itemlist = list(treeview.get_children(''))
        itemlist.sort(key=lambda x:treeview.set(x,col))
        for index, iid in enumerate(itemlist):
            treeview.move(iid,treeview.parent(iid),index)

class ShowImageForm(tk.Frame):
    """Display FIT file images"""

    def __init__(self,parent,settings,callbacks,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)

        self.settings = settings
        self.callbacks = callbacks

        # Build the form

        # image section
        imageinfo = tk.LabelFrame(
            self,
            text="Image Information",
            bg="khaki",
            padx=10,
            pady=10
        )

        # file selection

        # image display

        imageinfo.grid(row=0,column=0,sticky="we")