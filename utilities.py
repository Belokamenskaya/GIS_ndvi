import numpy as np
import glob

def read_mtl(path_tiff):
    mtl_file  = glob.glob(path_tiff + r'*MTL.txt') 
    
    data={}
    with open(mtl_file[0]) as file:
        for line in file:
            key, *value = line.split()
            data[key] = value
    return data

def landsat_to_reflectance(data, arr, band):
    print('работает landsat_to_reflectance,\n')
    sun = float(data['SUN_ELEVATION'][1])  
               
    Mult = float(data['REFLECTANCE_MULT_BAND_'+ str(band)][1])
    Add  = float(data['REFLECTANCE_ADD_BAND_'+ str(band)][1])
    c = arr*Mult + Add
    s = c/np.sin(sun)
    return s

def calcNDVI(b4, b5):
    '''
    NDVI = (NIR − RED)/(NIR + RED)
    landsat:
    NDVI = (Band 5 – Band 4) / (Band 5 + Band 4)

    Parameters
    ----------
    b5 : TYPE
        NIR channel.
    b4 : TYPE
        RED channel.

    Returns
    -------
    NDVI : TYPE
        NDVI.

    '''
    a = b5 - b4
    b = b5 + b4
    b[b == 0] = 1
    NDVI = np.divide(a,b)
    return NDVI

def calcNDWI(b3, b5):
    '''
    NDWI = (GREEN − NIR)/(GREEN + NIR)

    Returns
    -------
    NDWI : TYPE
        DESCRIPTION.

    '''
    a = b3 - b5
    b = b5 + b3
    b[b == 0] = 1
    NDWI = np.divide(a,b)
    return NDWI

def norm(band):
    '''
    Robust normalization

    Parameters
    ----------
    band : TYPE
        landsat band.

    Returns
    -------
    TYPE
        normalized band.

    '''
    hist = band.flatten()
    hist = np.sort(hist)
    band_min = hist[int(0.002 * hist.shape[0])]
    band_max = hist[int(0.998 * hist.shape[0])]
    return ((band - band_min)*255/(band_max - band_min)).astype(np.uint8)

def rgb(r, g, b):
    '''
    Landsat Natural Color (R = 4, G = 3, B = 2)

    Parameters
    ----------
    r : TYPE
        red channel.
    g : TYPE
        green channel.
    b : TYPE
        blue channel.

    Returns
    -------
    rgb : TYPE
        rgb image.

    '''
    r = norm(r)
    g = norm(g)
    b = norm(b)
    rgb = np.dstack((r, g, b))
    return rgb