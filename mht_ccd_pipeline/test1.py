import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
root=tk.Tk()
canvas = tk.Canvas(root)
canvas.pack(expand = tk.YES, fill = tk.BOTH)
x = np.linspace(0, 2*np.pi, 400)
y = np.linspace(0, 2*np.pi, 400)
X, Y = np.meshgrid(x, y, copy=False)
myarray = np.cos(X) + np.cos(Y)

im_plt = plt.imshow(myarray)

image1 = Image.fromarray(np.uint8( im_plt.get_cmap()(im_plt.get_array())*255))
im = ImageTk.PhotoImage('RGB', image1.size)
im.paste(image1)
test = canvas.create_image(0, 0, image=im)
tk.mainloop()