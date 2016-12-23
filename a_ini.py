import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import sys
from random import randint
import operator
from itertools import cycle
from collections import deque


img = cv2.imread(os.path.dirname(os.path.realpath(__file__))+'/MixedVegetables.jpg',0)
imgOrig = cv2.imread(os.path.dirname(os.path.realpath(__file__))+'/MixedVegetables.jpg')

gray = cv2.cvtColor(imgOrig, cv2.COLOR_BGR2GRAY)
(T, thresh) = cv2.threshold(gray, 128, 255, cv2.THRESH_TRUNC)
#
row,col = img.shape[0],img.shape[1]

nRow = row*2
nCol = col*2


crackImg = np.zeros((nRow,nCol))
crackImg3 = np.zeros((nRow,nCol,3))

i_img,j_img = 0,0
for i in range(nRow):
    for j in range(nCol):
        if(i % 2 == 0 and j % 2 == 0 and i_img < row and j_img < col):
            crackImg[i][j] = img[i_img][j_img]
            crackImg3[i][j] = imgOrig[i_img][j_img]            
            j_img += 1
        #else:
        #    crackImg[i][j] = 0
    
    if(i % 2 == 0):
        i_img += 1 
        j_img = 0                 


#Update Magnitude
crackNewImg = np.zeros((nRow,nCol))

T1 = 20

for i in range(nRow):
    for j in range(nCol):
        if(i % 2 != 0 or j % 2 != 0):
            
            if(i == 0):
                up = 0
            else:
                up = crackImg3[i-1][j]
            
            if(i+1 == nRow):
                down = 0
            else:
                down = crackImg3[i+1][j]            
            
            if(j == 0):                
                left = 0
            else:
                left = crackImg3[i][j-1]   
                
            if(j+1 == nCol):         
                right = 0
            else:
                right = crackImg3[i][j+1]            
                
            crackNewImg[i][j] = sum(np.abs(np.sqrt(np.square(left-right)+np.square(up-down))))
            #crackNewImg[i][j] = 255
            if(crackNewImg[i][j] < T1):
               crackNewImg[i][j] = 0
            else:
               crackNewImg[i][j] = 255 
            #print i,',',j,':',crackNewImg[i][j]
        else:
            crackNewImg[i][j] = crackImg[i][j]

#plt.subplot(122),plt.imshow(crackNewImg,cmap='gray')
#plt.title('Crack Edges normalized'), plt.xticks([]), plt.yticks([])
#
#plt.show()
#sys.exit()

re = np.zeros((nRow,nCol))
i_img,j_img = 0,0


temp = np.zeros((4,4))
temp[2][2] = 255
print nRow,nCol
#sys.exit()
def mergeRegionsNew(region,p,re):    
    
    queue = deque()
    queue.append(p)
    while(len(queue) > 0):
        r = [p[0],p[1]+2]
        if (r[0] < nRow and r[1] < nCol and re[p[0]][p[1]+2] == 0 and crackNewImg[p[0]][p[1]+1] == 0):
            region.append(r)
            queue.append(r)
            re[p[0]][p[1]+2] = 1
                    
        b = [p[0]+2,p[1]]
        if (b[0] < nRow and b[1] < nCol and re[p[0]+2][p[1]] == 0 and crackNewImg[p[0]+1][p[1]] == 0):
            region.append(b)
            queue.append(b)            
            re[p[0]+2][p[1]] = 1

        a = [p[0]-2,p[1]]
        if (a[0] > 0 and a[1] > 0 and re[p[0]-2][p[1]] == 0 and crackNewImg[p[0]-1][p[1]] == 0):
            region.append(a)
            queue.append(a)   
            re[p[0]-2][p[1]] = 1
    
    
        l = [p[0],p[1]-2]
        if (l[0] > 0 and l[1] > 0 and re[p[0]][p[1]-2] == 0 and crackNewImg[p[0]][p[1]-1] == 0):
            region.append(l)
            queue.append(l)   
            re[p[0]][p[1]-2] = 1
        
        p = queue.popleft()
    
        

allregions = []
regions = {}
cnt = 0
re = np.zeros((nRow,nCol))
for i in range(nRow):
    for j in range(nCol):
        region = []
        mergeRegionsNew(region,[i,j],re)
        if(len(region) > 0):
            regions[cnt] = region
            allregions.append(region)
            cnt += 1

allregions = np.array(allregions) 
newImage = np.full((nRow, nCol,3), 0)
cnt = 0         
colors = [25,50,75,100,125]
for v in allregions:
    
    #if(len(v)>10):
    #    print cnt,'->',len(v)
    color = [0,0,0]
    for j in v:
        color += imgOrig[j[0]/2][j[1]/2]
    
    color = color/len(v)
    
    #color = colors[cnt%5]
    for j in v:
        newImage[j[0]][j[1]] = color       
    cnt += 1


plt.subplot(111),plt.imshow(newImage[::2,::2])
plt.title('Region Merging'), plt.xticks([]), plt.yticks([])

plt.show()
