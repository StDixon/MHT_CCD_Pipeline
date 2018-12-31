import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

from astropy.utils.data import get_pkg_data_filename
from astropy.io import fits

root=tk.Tk()
canvas = tk.Canvas(root)
canvas.pack(expand = tk.YES, fill = tk.BOTH)
#x = np.linspace(0, 2*np.pi, 400)
#y = np.linspace(0, 2*np.pi, 400)
#X, Y = np.meshgrid(x, y, copy=False)
#myarray = np.cos(X) + np.cos(Y)

image_file = get_pkg_data_filename('tutorials/FITS-images/HorseHead.fits')
fits.info(image_file)
image_data = fits.getdata(image_file, ext=0)
print(image_data.shape)

im_plt = plt.imshow(image_data, cmap='gray')

#image1 = Image.fromarray(np.uint8( im_plt.get_cmap()(im_plt.get_array())*255))

im = ImageTk.PhotoImage('L',image_data.shape)

#im.paste(im_plt)
test = canvas.create_image(0, 0, image=im_plt)
tk.mainloop()