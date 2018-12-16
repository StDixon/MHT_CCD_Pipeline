#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 12:35:23 2018

@author: sdixon
"""

from tkinter import *
from tkinter import ttk

import configparser
import io

def newFile():
    #code here
    test == 1

def openFile():
   
    # Load the configuration file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # List all contents
    print("List all contents")
    for section in config.sections():
        print("Section: %s" % section)
        for options in config.options(section):
            print("x %s:::%s:::%s" % (options,
                                  config.get(section, options),
                                  str(type(options))))
    
def closeFile():
    #code here
    test == 3

def saveFile():
    config = configparser.ConfigParser()
    config['DEFAULT'] = {'ServerAliveInterval': '45',
                         'Compression': 'yes',
                         'CompressionLevel': '9'}
    config['bitbucket.org'] = {}
    config['bitbucket.org']['User'] = 'hg'
    config['topsecret.server.com'] = {}
    topsecret = config['topsecret.server.com']
    topsecret['Port'] = '50022'     # mutates the parser
    topsecret['ForwardX11'] = 'no'  # same here
    config['DEFAULT']['ForwardX11'] = 'yes'
    with open('example.ini', 'w') as configfile:
        config.write(configfile)
    
def saveasFile():
    #code here
    test == 5
    
def quitProg():
    #code here
    test == 6

def aboutProg():
    #code here
    test == 7
    
def _init_menu_file(bar,menu):
    bar.add_cascade(menu=menu_file, label='File', underline=0)
    
    menu.add_command(label='New', command=newFile, underline=0)
    menu.add_command(label='Open...', command=openFile, underline=0)
    menu.add_command(label='Close', command=closeFile, underline=0)
    menu.add_separator()
    menu.add_command(label='Save', command=saveFile, underline=0)
    menu.add_command(label='Save as...', command=saveasFile, underline=5)
    menu.add_separator()
    menu.add_command(label='Quit', command=quitProg, underline=0)

def _init_menu_edit(bar,menu):
    bar.add_cascade(menu=menu_edit, label='Edit', underline=0)
    

def _init_menu_help(bar,menu):
    bar.add_cascade(menu=menu_help, label='Help', underline=0)
    
    menu.add_separator()
    menu.add_command(label='About..', command=aboutProg, underline=0)
    
def _init_menu():
    menubar = Menu(win)
    menu_file = Menu(menubar)
    menu_edit = Menu(menubar)
    menu_help = Menu(menubar)
    
    _init_menu_file(menubar,menu_file)
    _init_menu_edit(menubar,menu_edit)
    _init_menu_help(menubar,menu_help)


    win['menu'] = menubar    
    
root=Tk()
root.option_add('*tearOff',FALSE)

root.withdraw()

win = Toplevel(root)
win.protocol("WM_DELETE_WINDOW", root.destroy)
win.title(' MHT CCD Pipeline ')

#but = Button(win, text='deiconify')
#but['command'] = root.deiconify
#but.pack()

_init_menu()

root.mainloop()




