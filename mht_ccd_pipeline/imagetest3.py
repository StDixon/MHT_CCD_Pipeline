import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import scipy as sp
import tkinter as tk
import PIL
from astropy.utils.data import download_file

image_file = download_file('http://data.astropy.org/tutorials/FITS-images/HorseHead.fits', cache=True )

hdulist = fits.open(image_file)
hdulist.info()
hdu = hdulist[0].data

histo = sp.histogram(hdu, 60, None, True) 
display_min = histo[1][0]
display_max = histo[1][1]
#pic = plt.imshow(scidata, cmap=plt.cm.gray, vmin=display_min, vmax=display_max, origin="lower")
#plt.imsave("tempimgfile.png", hdu.data, cmap=plt.cm.gray, vmin=display_min, vmax=display_max, origin="lower")
plt.imsave("tempimgfile1.png", hdu, origin="lower")

#Try tk stuff
root = tk.Tk()

#setting up a tkinter canvas
frame = tk.Frame(root, bd=2, relief=tk.SUNKEN)
frame.grid_rowconfigure(0, weight=1)
frame.grid_columnconfigure(0, weight=1)
canvas = tk.Canvas(frame, bd=0)
canvas.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
frame.pack(fill=tk.BOTH,expand=1)

#Add image
#hold = tk.PhotoImage(pic)
hold = tk.PhotoImage(file="tempimgfile1.png")
canvas.create_image(0,0,image=hold,anchor="nw")

#function to be called when mouse is clicked
def printcoords(event):
    #outputting x and y coords to console
    print (event.x,event.y)
#mouseclick event
canvas.bind("<Button 1>",printcoords)

root.mainloop()

hdulist.close()