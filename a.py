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


#img = cv2.imread(os.path.dirname(os.path.realpath(__file__))+'/MixedVegetables.jpg',0)
#imgOrig = cv2.imread(os.path.dirname(os.path.realpath(__file__))+'/MixedVegetables.jpg')
imgOrig = cv2.imread(os.path.dirname(os.path.realpath(__file__))+'/mvthumb.jpg')
img = cv2.imread(os.path.dirname(os.path.realpath(__file__))+'/mvthumb.jpg',0)

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
allcnt = 0
re = np.zeros((nRow,nCol))
for i in range(nRow):
    for j in range(nCol):
        region = []
        mergeRegionsNew(region,[i,j],re)
        if(len(region) > 0):
            allcnt += len(region)
            regions[cnt] = region
            allregions.append(region)
            cnt += 1

print allcnt
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
#sys.exit()        



# Code is implemented for merging the regions using the W/min(l1,l2) formula 
# but it is not optimized so it doesn't work for the full image

#New Threshold
def get_distance(x, y):
    """ use pythagorean theorm to find distance between 2 points """
    a = x[0] - y[0]
    b = x[1] - y[1]
    c_2 = a*a + b*b

    return c_2 ** (1/2)

def get_distances(points):
    """ convert a list of points into a list of distances """

    circular_buffer = cycle(points)
    previous_point  = circular_buffer.next()

    for i in range(len(points)):
        point = circular_buffer.next()
        yield get_distance(previous_point, point)
        previous_point = point

def get_perimeter(points):
    """ returns the length of the perimiter of some shape defined by a list of points """

    return sum(get_distances(points))
    
#Calculate number of weak edges on the common boundary
def calcW(r1,r2):
    
    W = 0
    if(len(r1) == 0 or len(r2) == 0):
        return W
    for v in r1:
        if ( ([v[0],v[1]+2] in r2) ):
                W += 1
        
        if ( ([v[0]+2,v[1]] in r2) ):
                W += 1
                
    #print "R1",len(r1)
    #print "R2",len(r2)
    #print "W",W
    #sys.exit()
                
    return W   

def calcL(r):
    
    L = []
    if(len(r) == 0):
        return L
    
    #for i in r:
    #    del i
    
    for i in r:
        if not( ([i[0],i[1]-2] in r) and ([i[0]-2,i[1]] in r) and ([i[0],i[1]+2] in r) and ([i[0]+2,i[1]] in r) ):
            #L += 1
            L.append([i[0],i[1]])
            
    return L


T2 = 0.001

def mergeRegions():    
    
    lenI = len(regions)
    lenR = len(regions)  
    tempI = 0 
    L = []
    for i in regions.iterkeys():
        lRi = calcL(regions[i])
        L.append(lRi)
        
    newregions = {}
    for i in regions.iterkeys():
        Li = calcL(regions[i])
        li = len(Li)
        if(len(regions[i])>0):
            for j in range(i+1,lenR):
                if(j in regions):
                    Lj = calcL(regions[j])
                    lj = (Lj)
                    W = calcW(Li,Lj)   
    
                    #print i,j,li,lj
                                    
                    val = 0
                    if(li > 0 and lj > 0):
                        val = float(W)/min(li,lj)
                    
                    if(val < 1 and val > 0):
                        print 'W/min(li,lj):',val
                    #print val
                    if(val >= T2):
                        #if(i in newregions):
                        #    newregions[i] = regions[i] + regions[j]
                        #else:
                        #    newregions[i] = newregions[i] + regions[j]
                        regions[i] = regions[i] + regions[j]                    
                        lRi = calcL(regions[i])
                        li = len(lRi)
                        regions[j] = {} 
                        tempI = j
                #print i,j
        #i = tempI
    #global regions
    #regions = newregions
    #lenIni = i      
    lenFinal = 0  
    for i in regions.keys():
        lenR = len(regions[i])
        #print i,'->',lenR
        if(lenR > 0):
            lenFinal += 1
        else:
            del regions[i]
    
    print "LenIni:",lenI,"LenFinal:",lenFinal  
            
    if(lenFinal < lenI):
       lenI = lenFinal 
       mergeRegions() 

print "MergeRegions",len(regions)
mergeRegions()


for k in regions.keys():
    if(len(regions[k]) == 0):
        del regions[k]


newImage = np.full((nRow, nCol), 0)
color = 50
for k,v in regions.iteritems():
    color = crackNewImg[v[0][0]][v[0][1]]
    for i in range(len(v)):
        if(v[i][0] < nRow and v[i][1] < nCol):
            newImage[v[i][0]][v[i][1]] = color

plt.subplot(122),plt.imshow(newImage[::2, ::2])
plt.title('Crack Edges normalized'), plt.xticks([]), plt.yticks([])

plt.show()
        