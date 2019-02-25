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
            label='Open file...',
            command=self.callbacks['file->open'],
            accelerator='Ctrl-O'
        )
        file_menu.add_command(
            label='Save',
            command=self.callbacks['file->save'],
            accelerator='Ctrl-S'
        )
        file_menu.add_command(
            label='Save as...',
            command=self.callbacks['file->saveas'],
            accelerator='Ctrl-A'
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

        # Show Headers
        go_menu.add_command(
            label='Show Image File',
            command=self.callbacks['go->imagefile']
        )

        # Perform Reduction
        go_menu.add_command(
            label='CCD Reduction',
            command=self.callbacks['go->ccdreduction']
        )

        self.add_cascade(label='Go',menu=go_menu)

        # Preferences menu
        pref_menu = tk.Menu(self,tearoff=False)

        # Settings sub menu
        settings_menu = tk.Menu(self,tearoff=False)

        # Font sub-sub menu
        font_size_menu = tk.Menu(self,tearoff=False)
        for size in range(6,17,1):
            font_size_menu.add_radiobutton(
                label=size,
                value=size,
                variable=self.settings['font size']
            )
        settings_menu.add_cascade(label='Font size',menu=font_size_menu)

        # Theme sub-sub menu
        style = ttk.Style()
        themes_menu = tk.Menu(self,tearoff=False)
        for theme in style.theme_names():
            themes_menu.add_radiobutton(
                label=theme,
                value=theme,
                variable=self.settings['theme']
            )
        settings_menu.add_cascade(label='Theme',menu=themes_menu)

        self.settings['theme'].trace('w',self.on_theme_change)

        pref_menu.add_cascade(label='Settings',menu=settings_menu)

        # Config sub menu
        config_menu = tk.Menu(self,tearoff=False)

        # Directories sub-sub menu
        config_menu.add_command(
            label='Directories',
            command=self.callbacks['conf->directories']
        )

        # General sub-sub menu
        config_menu.add_command(
            label='General',
            command=self.callbacks['conf->general']
        )

        # Bias sub-sub menu
        config_menu.add_command(
            label='Bias Details',
            command=self.callbacks['conf->biasdetails']
        )

        # Dark sub-sub menu
        config_menu.add_command(
            label='Dark Details',
            command=self.callbacks['conf->darkdetails']
        )

        # Flat sub-sub menu
        config_menu.add_command(
            label='Flat Details',
            command=self.callbacks['conf->flatdetails']
        )

        # Science sub-sub menu
        config_menu.add_command(
            label='Science Details',
            command=self.callbacks['conf->sciencedetails']
        )

        # Master sub-sub menu
        config_menu.add_command(
            label='Master Details',
            command=self.callbacks['conf->masterdetails']
        )

        # Reduction sub-sub menu
        config_menu.add_command(
            label='Reduced Details',
            command=self.callbacks['conf->reduceddetails']
        )

        pref_menu.add_cascade(label='Configuration',menu=config_menu)

        self.add_cascade(label='Preferences',menu=pref_menu)

        # Help menu
        help_menu = tk.Menu(self,tearoff=False)

        help_menu.add_command(
            label='Help',
            command=self.show_about
        )
        self.add_cascade(label='Help',menu=help_menu)

    def get_keybinds(self):
        return{
            '<Control-o>':self.callbacks['file->open'],
            '<Control-s>':self.callbacks['file->save'],
            '<Control-a>':self.callbacks['file->saveas'],
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

    def on_theme_change(self,*args):
        """Popup a message about theme changes"""
        message = "Change requires restart"
        detail = (
            "Theme changes do not take effect"
            " until application restart")
        messagebox.showwarning(
            title='Warning',
            message=message,
            detail=detail)

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