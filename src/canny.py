#!/usr/bin/env python
#******************************************************************************
#  Name:     canny.py
#  Purpose:  Principal components analysis
#  Usage (from command line):             
#    python canny.py  [-d spatial subset] [-b spectral band] fileNmae
#
#    calculate Canny edges
#
#  Copyright (c) 2015, Mort Canty
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
import auxil.auxil as auxil
import numpy as np
from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly, GDT_Byte
import cv2 as cv 
import matplotlib.pyplot as plt
import getopt,sys,os,time
  
def main(): 
    usage = '''Usage: python %s  [-d dims] [-b spectral band] fileName\n
            spatial subset is a list, e.g., -d [0,0,400,400] \n'''%sys.argv[0]
    options,args = getopt.getopt(sys.argv[1:],'hd:p:')
    dims = None
    b = 1
    for option, value in options: 
        if option == '-h':
            print usage
            return 
        elif option == '-d':
            dims = eval(value)  
        elif option == '-b':
            b = eval(value)    
    gdal.AllRegister() 
    infile = args[0]           
    path = os.path.dirname(infile)
    basename = os.path.basename(infile)
    root, ext = os.path.splitext(basename)
    outfn = path + '/' + root + '_edges' + ext        
    inDataset = gdal.Open(infile,GA_ReadOnly)     
    cols = inDataset.RasterXSize
    rows = inDataset.RasterYSize    
    if dims:
        x0,y0,cols,rows = dims
    else:
        x0 = 0
        y0 = 0        
#  read b'th band of MS image  
    rasterBand = inDataset.GetRasterBand(b) 
    band = rasterBand.ReadAsArray(0,0,cols,rows)    
    start = time.time()                          
#  find and display contours    
    edges = cv.Canny(band, 20, 80)    
    contours,hierarchy = cv.findContours(edges,cv.RETR_LIST,cv.CHAIN_APPROX_NONE)
    arr = np.zeros((rows,cols),dtype=np.uint8)
    cv.drawContours(arr, contours, -1, 255)
    
    driver = inDataset.GetDriver()    
    outDataset = driver.Create(outfn,cols,rows,1,GDT_Byte)
    projection = inDataset.GetProjection()
    geotransform = inDataset.GetGeoTransform()
    if geotransform is not None:
        gt = list(geotransform)
        gt[0] = gt[0] + x0*gt[1]
        gt[3] = gt[3] + y0*gt[5]
        outDataset.SetGeoTransform(tuple(gt))
    if projection is not None:
        outDataset.SetProjection(projection)             
    outBand = outDataset.GetRasterBand(1)
    outBand.WriteArray(arr,0,0)
    outBand.FlushCache()
    inDataset=None
    outDataset=None
    print 'Edges image written to: %s'%outfn
    print 'elapsed time: %s'%str(time.time()-start)

if __name__ == '__main__':
    main()    