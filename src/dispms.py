#!/usr/bin/env python
#******************************************************************************
#  Name:     dispms.py
#  Purpose:  Display a multispectral image
#             allowed formats: uint8, uint16,float32,float64 
#  Usage (from command line):             
#    python dispms.py [-f filename, -d spatialDimensions -p RGB band positions -e enhancement method]
#
#  Copyright (c) 2011, Mort Canty
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

import sys, getopt, gdal
import matplotlib.pyplot as plt
import  auxil.auxil as auxil 
import numpy as np
from osgeo.gdalconst import GA_ReadOnly

def dispms(filename=None,dims=None,rgb=None,enhance=None):
    gdal.AllRegister()
    if filename == None:        
        filename = raw_input('Enter an image to display: ') 
    try:                  
        inDataset = gdal.Open(filename,GA_ReadOnly) 
        cols = inDataset.RasterXSize    
        rows = inDataset.RasterYSize    
        bands = inDataset.RasterCount
    except Exception as e:
        print 'Error in dispms: %s'%e
        return   
    if dims == None:
        dims = [0,0,cols,rows]
    if dims:
        x0,y0,cols,rows = dims
    else:
        return
    if rgb == None:
        rgb = [1,1,1]
    if rgb:
        r,g,b = rgb
    else:
        return
    if enhance == None:
        enhance = 3
    if enhance == 1:
        enhance = 'linear255'
    elif enhance == 2:
        enhance = 'linear'
    elif enhance == 3:
        enhance = 'linear2pc'
    elif enhance == 4:
        enhance = 'equalization'
    else:
        return    
    redband   = inDataset.GetRasterBand(r).ReadAsArray(x0,y0,cols,rows)
    greenband = inDataset.GetRasterBand(g).ReadAsArray(x0,y0,cols,rows)  
    blueband  = inDataset.GetRasterBand(b).ReadAsArray(x0,y0,cols,rows)
    if str(redband.dtype) == 'uint8':
        dt = 1
    elif str(redband.dtype) == 'uint16':
        dt = 2
    elif str(redband.dtype) == 'int16':
        dt = 2        
    elif str(redband.dtype) == 'float32':
        dt = 4
    elif str(redband.dtype) == 'float64':
        dt = 6
    else:
        print 'Unrecognized format'
        return   
    redband = redband.tostring()
    greenband = greenband.tostring()
    blueband = blueband.tostring()
    if dt != 1: 
        redband   = auxil.byte_stretch(redband,dtype=dt)
        greenband = auxil.byte_stretch(greenband,dtype=dt)
        blueband  = auxil.byte_stretch(blueband,dtype=dt)        
    r,g,b = auxil.stretch(redband,greenband,blueband,enhance)  
    X = np.zeros((rows*cols,3),dtype=np.float32)                                                                                                                 
    X[:,0] = np.float32(np.fromstring(r,dtype=np.uint8))
    X[:,1] = np.float32(np.fromstring(g,dtype=np.uint8))
    X[:,2] = np.float32(np.fromstring(b,dtype=np.uint8))
    X = np.reshape(X,(rows,cols,3))/255.
    f, ax = plt.subplots(figsize=(10,10))
    ax.imshow(X)
    ax.set_title(filename)
    plt.show()
                       

def main():
    usage = '''Usage: python %s [-f filename] [-p pos] [-d dims] [-e enhancement]
                  RGB bandPositions and spatialDimensions are lists, e.g., -p [0,1,3] -d [0,0,400,400] \n
                  enhancements: 1=linear255 2=linear 3=linear2pc 4=equalization\n'''%sys.argv[0]
    options,args = getopt.getopt(sys.argv[1:],'hf:p:d:e:')
    filename = None
    dims = None
    rgb = None
    enhance = None   
    for option, value in options: 
        if option == '-h':
            print usage
            return 
        elif option == '-f':
            filename = str(value)
        elif option == '-p':
            rgb = tuple(eval(value))
        elif option == '-d':
            dims = eval(value) 
        elif option == '-e':
            enhance = eval(value)  
    dispms(filename,dims,rgb,enhance)

if __name__ == '__main__':
    main()