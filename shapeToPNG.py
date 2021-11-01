import numpy as np
from osgeo import ogr, gdal

def shapeToPNG_GDAL(file_name, RefImage):  
    name_png = file_name.split('/')[-1].split('.')[0]
    InputVector = file_name
    OutputImage = 'Result.tif'
    
    gdalformat = 'GTiff'
    datatype = gdal.GDT_Byte
    burnVal = 1 #value for the output image pixels
    ##########################################################
    # Get projection info from reference image
    Image = gdal.Open(RefImage, gdal.GA_ReadOnly)
     
    # Open Shapefile
    Shapefile = ogr.Open(InputVector)
    Shapefile_layer = Shapefile.GetLayer()
    
    # Rasterise
    # print("Rasterising shapefile...")
    Output = gdal.GetDriverByName(gdalformat).Create(OutputImage, Image.RasterXSize, Image.RasterYSize, 1, datatype, options=['COMPRESS=DEFLATE'])
    Output.SetProjection(Image.GetProjectionRef())
    Output.SetGeoTransform(Image.GetGeoTransform()) 
    
    # Write data to band 1
    Band = Output.GetRasterBand(1)
    Band.SetNoDataValue(0)
    # gdal.RasterizeLayer(Output, [1], Shapefile_layer, burn_values=[burnVal])
    gdal.RasterizeLayer(Output, [1], Shapefile_layer, options=["ALL_TOUCHED=TRUE"])
    Output.GetRasterBand(1).SetNoDataValue(0.0) 
    band = Output.GetRasterBand(1)
    # arr  = band.ReadRaster(xoff=0, yoff=0, xsize=band.XSize, ysize=1, buf_xsize=band.XSize, buf_ysize=1, buf_type=gdal.GDT_Float32)
    arr = band.ReadAsArray()
    arr.astype(np.uint8)
    
    
    # Close datasets
    Band = None
    Output = None
    Image = None
    Shapefile = None
    
    return arr



