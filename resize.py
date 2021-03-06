import os
import PIL
from PIL import Image

basewidth = 100
dirPath = os.path.dirname(os.path.realpath(__file__))
img = Image.open(dirPath+'/MixedVegetables.jpg')
wpercent = (basewidth/float(img.size[0]))
hsize = int((float(img.size[1])*float(wpercent)))
img = img.resize((basewidth,hsize), PIL.Image.ANTIALIAS)
img.save(dirPath+'/mvthumb.jpg') 
