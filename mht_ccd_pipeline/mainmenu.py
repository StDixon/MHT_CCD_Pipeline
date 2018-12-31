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
            label='Show Image File',
            command=self.callbacks['go->imagefile']
        )
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

        # File Location sub-sub menu
        file_loc_menu = tk.Menu(self,tearoff=False)

        config_menu.add_cascade(label='File locations',menu=file_loc_menu)

        # Master names sub-sub menu
        master_names_menu = tk.Menu(self,tearoff=False)

        config_menu.add_cascade(label='Master names',menu=master_names_menu)

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