import matplotlib.pyplot as plt
from astropy.io import fits
#import cv2
headerList=fits.open('samples/M33-0003V.fit')
#Load table data as image data
#imgData = headerList[1].data 
imgData = headerList[0].data 

hdu=headerList[0]
print('shape :',hdu.shape) #shape is 1024*1024

#show image
#plt.figure()
plt.imshow(hdu.data)
plt.show()