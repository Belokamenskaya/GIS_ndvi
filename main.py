import glob
import numpy as np
import tifffile
import matplotlib.pyplot as plt

from utilities import *
from shapeToPNG import shapeToPNG_GDAL


prefix = "E:/GIS/trees_data/"
folder_path = prefix + r'LC08_L1TP_175021_20200409_20200409_01_RT/'

NN_c = (2750, 6700)
NN_r = 800

# NDVI = (Band 5 – Band 4) / (Band 5 + Band 4)
# Landsat Natural Color (R = 4, G = 3, B = 2)
bands = [2,3,4,5]
 
tiff = glob.glob(folder_path + '*.TIF')
#поправка на рефлектанс
reflectance_files = glob.glob(folder_path + '*.npy')

patches = {}

if len(reflectance_files) < len(bands):
    mtl = read_mtl(folder_path)
    #  all tif 1 - 12 channels
    for  file in tiff:
        for b in bands:
            if file.find("_B" + str(b)) > -1:
                arr = tifffile.imread(file, key=0)
                patch = arr[NN_c[0] - NN_r:NN_c[0] + NN_r, NN_c[1] - NN_r:NN_c[1] + NN_r]    
                reflectance = landsat_to_reflectance(mtl, patch, b)
                np.save(folder_path + str(b), reflectance)
                patches[b] = reflectance
                break
else:
    for file in reflectance_files:
        for b in bands:
            if file.find(str(b)+".npy") > -1:
                patch = np.load(file)
                patches[b] = patch
                break


rgb = rgb(patches[4], patches[3], patches[2])

plt.imshow(rgb)
plt.title("rgb")
plt.show()

ndvi = calcNDVI(patches[4], patches[5])
plt.title("ndvi")
plt.imshow(ndvi, cmap = 'gray')
plt.show()
    


#  name, people, km^2
districts = { 'sovetsky':       ['sovetsky',  148909, 31],
              'sormovsky':      ['sormovsky', 166996, 100],
              'prioksky' :      ['prioksky',  94956, 23],
              'nizhegorodsky' : ['nizhegorodsky', 132425, 67],
              'moscow' :        ['moscow', 124515, 30],
              'leninsky' :      ['leninsky', 141738, 141738],
              'kanavinsky' :    ['kanavinsky', 158000, 48],
              'avtozavodsky':   ['avtozavodsky', 300436, 94]} 
    
ndvi_t = np.zeros(ndvi.shape)

critical = 0.25
ndvi[ndvi > critical] = 1
ndvi[ndvi < critical] = 0

#  thinitial resolution is nessesary
test = tifffile.imread(tiff[0], key=0)   

# districs mask visualization
step = int(256 / (len(districts) + 1))
all_mask = np.zeros(ndvi.shape)

path_shape=r'districts/'

plants_y = []
perperson_y = []

for district, i in zip(districts, range(step, 256, step)):   
      
    shapename = path_shape + district + "/" + district + ".shp" 
    mask = shapeToPNG_GDAL(shapename, tiff[0])    
    mask =  mask[NN_c[0] - NN_r:NN_c[0] + NN_r, NN_c[1] - NN_r:NN_c[1] + NN_r]

    np.putmask(all_mask, mask > 0, np.uint16(i*200))
             
    ndvi_t = np.copy(ndvi)
    np.putmask(ndvi_t, mask == 0, 0)
         
    area = np.sum(mask)
    plants = np.sum(ndvi_t)
    
    plants_y.append(plants * 100/area)
    perperson_y.append(plants / districts[district][1])
    print(district, '{:.1%}'.format(plants * 100/area))
    print(district, 'per person {:.1f}'.format(plants / districts[district][1]))


plt.title("all_mask")
plt.imshow(all_mask, cmap = 'gray')
plt.show()
           
labels = districts.keys()

#  Offset equals 1/2 bar width
fig, ax = plt.subplots()
x1 = np.arange(0, len(labels)) - 0.2
x2 = np.arange(0, len(labels)) + 0.2
ax.set_xticks([0, 1, 2, 3, 4, 5, 6, 7])
ax.set_xticklabels(labels)
ax.bar(x1, plants_y, width = 0.4)
ax.bar(x2, perperson_y, width = 0.4)
legend = ['Area', 'Per Person']
plt.legend(legend, loc=2)
ax.set_facecolor('seashell')
fig.set_figwidth(12)    #  ширина Figure
fig.set_figheight(6)    #  высота Figure
fig.set_facecolor('floralwhite')
plt.title("Plants persent")
plt.show()

