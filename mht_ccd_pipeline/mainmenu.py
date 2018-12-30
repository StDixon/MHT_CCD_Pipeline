import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from functools import partial

class GenericMainMenu(tk.Menu):
    """The Application's main menu"""

    def __init__(self,parent,settings,callbacks,**kwargs):
        """Main menu constructor
        
        arguments:
          parent - The parent
          settings - a dict containing Tkinter variables
          callbacks - a dict containing Python callables
        """
        super().__init__(parent,**kwargs)
        self.settings = settings
        self.callbacks = callbacks
        self._build_menu()
        self._bind_accelerators()

    def _build_menu(self):

        # File menu
        file_menu = tk.Menu(self,tearoff=False)

        file_menu.add_command(
            label='Select file...',
            command=self.callbacks['file->select'],
            accelerator='Ctrl-O'
        )
        file_menu.add_separator()
        file_menu.add_command(
            label='Quit',
            command=self.callbacks['file->quit'],
            accelerator='Ctrl-Q'
        )
        self.add_cascade(label='File',menu=file_menu)

        # Go menu
        go_menu = tk.Menu(self,tearoff=False)

        go_menu.add_command(
            label='Show Headers',
            command=self.callbacks['go->headers']
        )
        go_menu.add_command(
            label='Show Images',
            command=self.callbacks['go->images']
        )
        self.add_cascade(label='Go',menu=go_menu)

        # Help menu
        help_menu = tk.Menu(self,tearoff=False)

        help_menu.add_command(
            label='Help',
            command=self.show_about
        )
        self.add_cascade(label='Help',menu=help_menu)

    def get_keybinds(self):
        return{
            '<Control-o>':self.callbacks['file->select'],
            '<Control-q>':self.callbacks['file->quit'],
        }

    @staticmethod
    def _argstrip(function,*args):
        return function()

    def _bind_accelerators(self):
        keybinds = self.get_keybinds()
        for key, command in keybinds.items():
            self.bind_all(
                key,
                partial(self._argstrip,command)
            )

    def show_about(self):
        """Show the about dialog"""

        about_message = 'MHT CCD Reduction'
        about_detail = (
            'by Stephen Dixon\n'
            'For assistance please contact the author.'
        )
        messagebox.showinfo(
            title='About',
            message=about_message,
            detail=about_detail
        )

class LinuxMainMenu(GenericMainMenu):
    """Differences for Linux:"""
    pass

class WindowsMainMenu(GenericMainMenu):
    """Differences for Windows:"""
    pass

class MacOsMainMenu(GenericMainMenu):
    """Differences for MacOS:"""
    pass

def get_main_menu_for_os(os_name):
    menus = {
        'Linux': LinuxMainMenu,
        'Darwin': MacOsMainMenu,
        'freebsd7': LinuxMainMenu,
        'Windows': WindowsMainMenu
    }

    return menus.get(os_name,GenericMainMenu)