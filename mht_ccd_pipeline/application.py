import platform
import os
from os import environ
from datetime import datetime
from pathlib import Path

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

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

        # header model
        datestring = datetime.today().strftime("%Y-%m-%d")
        default_filename = "mht_data_record_{}.csv".format(datestring)
        self.filename = tk.StringVar(value=default_filename)
        self.header_model = m.HeaderModel(filename=self.filename.get())

        self.settings = {}
        self.callbacks = {
            'file->select':self.on_file_select,
            'file->quit':self.quit,
            'go->headers':self.show_headers,
            'go->images':self.show_images,
            'on_open_file_header':self.open_file_header,
        }

        # Menu
        menu_class = get_main_menu_for_os(platform.system())
        menu = menu_class(self,self.settings,self.callbacks)
        self.config(menu=menu)

        # Header view form
        self.headerform = v.ShowHeaderForm(
            self,
            m.HeaderModel.fields,
            self.settings,
            self.callbacks
        )
        self.headerform.grid(row=0,padx=10,sticky='NSEW')
        #self.populate_headerform()

        # Image view form
        self.imageform = v.ShowImageForm(
            self,
            self.settings,
            self.callbacks
        )
        self.imageform.grid(row=0,padx=10,sticky='NSEW')



    def on_file_select(self):
        """Handle the file->select action from the menu"""
        pass

    def show_headers(self):
        """Handle the go->headers action from the menu"""
        self.populate_headerform()
        self.headerform.tkraise()

    def show_images(self):
        """Handle the go->images action from the menu"""
        self.imageform.tkraise()

    def open_file_header(self,filename=None):
        if filename is None:
            header = None
        else:
            try:
                header = self.data_model.get_header(filename)
            except Exception as e:
                messagebox.showerror(
                    title='Error',
                    message='Problem reading file',
                    detail=str(e)
                )
                return
        self.headerform.load_header(filename,header)
        self.headerform.tkraise()

    def populate_headerform(self):
        
        working_path = '.'
        image_path = 'samples'
        default_path = os.path.join(working_path,image_path)
        files = Path(default_path).glob('**/*.fit')

        rows = []

        for file in files:
            path = str(file)
            filename = str(file.name)
            parent = str(file.parent)
            if parent == '.' or parent == image_path:
                parent = ''
            row = {'Filename':filename,'Parent':parent,'Path':path}
            rows.append(row)

        self.headerform.populate_header(rows)
