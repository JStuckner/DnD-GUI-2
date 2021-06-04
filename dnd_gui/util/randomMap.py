from random import randint
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage, misc
import imageio
from skimage.transform import resize

def string_to_array(string, height=30, color=255):
    array = np.zeros((height, 1))
    size = int(round(height/10))
    for i in range(len(string)):
        nex = char_to_array(string[i],color)
        nex = np.repeat(np.repeat(nex, size, axis=0), size, axis=1)
        array = np.append(array, nex, axis=1)
    return array


#rollTable(('spells','mage3','5'))
def create(xsize,ysize,items,xloc=0,yloc=0,get=False):

    pix = 50 #pixels per unit

    #Load background map
    background = imageio.imread(r'maps\Elin.jpg')
    back_unit_width = 68
    back_unit_height = 60
    #background = misc.imresize(background,(back_unit_height*pix*6,back_unit_width*pix*6))

    xmin = int(xloc * 100)
    xmax = int((xloc + xsize / 6) * 100)
    ymin = int(yloc * 100)
    ymax = int((yloc + ysize / 6) * 100)
    print(xmin, xmax, ymin, ymax)
    zoom = background[xmin:xmax, ymin:ymax, :]
    zoom = resize(zoom, (xsize*50, ysize*50))
    print(xmin, xmax, ymin, ymax)


    Map = np.ones((xsize*pix,ysize*pix))
    print(xmin, xmax, ymin, ymax)
    for i in range(ysize):
        zoom[:,pix*i,:] = 0

    for i in range(xsize):
        zoom[pix*i,:,:] = 0


    for i in range(items):
        xloc = randint(0,xsize-1)
        yloc = randint(0,ysize-1)
        num = string_to_array(str(i+1), height=20, color=255)
        num = 255 - num #invert 1s and 0s.
        if i < 9:
            y = yloc*pix+10
        else:
            y = yloc*pix+1
        x = xloc*pix+10
        xl,yl = num.shape
        zoom[x:x+xl,y:y+yl,0] = num
        zoom[x:x+xl,y:y+yl,1] = num
        zoom[x:x+xl,y:y+yl,2] = num


    if not get:
        plt.imshow(zoom)
        plt.show()

    if get:
        return zoom

#x = create(20,20,15,34,16,get=False)
