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

def make_image(redband,greenband,blueband,rows,cols,enhance):
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
    if enhance == 'linear255':
        rng = [0.0,255.0]
    else:
        rng = None
    if dt != 1: 
        redband   = auxil.byte_stretch(redband,dtype=dt,rng=rng)
        greenband = auxil.byte_stretch(greenband,dtype=dt,rng=rng)
        blueband  = auxil.byte_stretch(blueband,dtype=dt,rng=rng)        
    r,g,b = auxil.stretch(redband,greenband,blueband,enhance)  
    X = np.zeros((rows*cols,3),dtype=np.float32)                                                                                                                 
    X[:,0] = np.float32(np.fromstring(r,dtype=np.uint8))
    X[:,1] = np.float32(np.fromstring(g,dtype=np.uint8))
    X[:,2] = np.float32(np.fromstring(b,dtype=np.uint8))
    return np.reshape(X,(rows,cols,3))/255.

def dispms(filename1=None,filename2=None,dims=None,DIMS=None,rgb=None,RGB=None,enhance=None,ENHANCE=None,cls=False,CLS=False):
    gdal.AllRegister()
    if filename1 == None:        
        filename1 = raw_input('Enter image filename: ')
    inDataset1 = gdal.Open(filename1,GA_ReadOnly)    
    try:                   
        cols = inDataset1.RasterXSize    
        rows = inDataset1.RasterYSize  
        bands1 = inDataset1.RasterCount  
    except Exception as e:
        print 'Error in dispms: %s  --could not read image file'%e
        return   
    if filename2 is not None:                
        inDataset2 = gdal.Open(filename2,GA_ReadOnly) 
        try:       
            cols2 = inDataset2.RasterXSize    
            rows2 = inDataset2.RasterYSize            
            bands2 = inDataset2.RasterCount       
        except Exception as e:
            print 'Error in dispms: %s  --could not read second image file'%e
            return       
    if dims == None:
        dims = [0,0,cols,rows]
    x0,y0,cols,rows = dims
    if rgb == None:
        rgb = [1,1,1]
    r,g,b = rgb
    r = np.min([r,bands1])
    g = np.min([g,bands1])
    b = np.min([b,bands1])
    
    if enhance == None:
        enhance = 2
    if enhance == 1:
        enhance = 'linear255'
    elif enhance == 2:
        enhance = 'linear'
    elif enhance == 3:
        enhance = 'linear2pc'
    elif enhance == 4:
        enhance = 'equalization'
    else:
        enhance = 'linear2pc' 
    try:  
        if not cls:
            redband   = np.nan_to_num(inDataset1.GetRasterBand(r).ReadAsArray(x0,y0,cols,rows))
            greenband = np.nan_to_num(inDataset1.GetRasterBand(g).ReadAsArray(x0,y0,cols,rows)) 
            blueband  = np.nan_to_num(inDataset1.GetRasterBand(b).ReadAsArray(x0,y0,cols,rows))
        else:
            classimg = inDataset1.GetRasterBand(1).ReadAsArray(x0,y0,cols,rows).ravel()
            ctable = np.reshape(auxil.ctable,(18,3))
            classes = range(1,np.max(classimg)+1)
            redband = classimg*0
            greenband = classimg*0
            blueband = classimg*0
            for k in classes:
                idx = np.where(classimg==k)
                redband[idx] = ctable[k-1,0]
                greenband[idx] = ctable[k-1,1]
                blueband[idx] = ctable[k-1,2]
            redband = np.reshape(redband,(rows,cols))    
            greenband = np.reshape(greenband,(rows,cols))
            blueband = np.reshape(blueband,(rows,cols))
        inDataset = None   
    except  Exception as e:
        print 'Error in dispms: %s'%e  
        return
    X1 = make_image(redband,greenband,blueband,rows,cols,enhance)
    if filename2 is not None:
        if DIMS == None:
            DIMS = [0,0,cols2,rows2]
        x0,y0,cols,rows = DIMS
        if RGB == None:
            RGB = rgb
        r,g,b = RGB
        r = np.min([r,bands2])
        g = np.min([g,bands2])
        b = np.min([b,bands2])
        enhance = ENHANCE
        if enhance == None:
            enhance = 2
        if enhance == 1:
            enhance = 'linear255'
        elif enhance == 2:
            enhance = 'linear'
        elif enhance == 3:
            enhance = 'linear2pc'
        elif enhance == 4:
            enhance = 'equalization'
        else:
            enhance = 'linear2pc'          
        try:  
            if not CLS:
                redband   = np.nan_to_num(inDataset2.GetRasterBand(r).ReadAsArray(x0,y0,cols,rows))
                greenband = np.nan_to_num(inDataset2.GetRasterBand(g).ReadAsArray(x0,y0,cols,rows)) 
                blueband  = np.nan_to_num(inDataset2.GetRasterBand(b).ReadAsArray(x0,y0,cols,rows))
            else:
                classimg = inDataset2.GetRasterBand(1).ReadAsArray(x0,y0,cols,rows).ravel()
                ctable = np.reshape(auxil.ctable,(18,3))
                classes = range(1,np.max(classimg)+1)
                redband = classimg*0
                greenband = classimg*0
                blueband = classimg*0
                for k in classes:
                    idx = np.where(classimg==k)
                    redband[idx] = ctable[k-1,0]
                    greenband[idx] = ctable[k-1,1]
                    blueband[idx] = ctable[k-1,2]
                redband = np.reshape(redband,(rows,cols))    
                greenband = np.reshape(greenband,(rows,cols))
                blueband = np.reshape(blueband,(rows,cols))
            inDataset = None   
        except  Exception as e:
            print 'Error in dispms: %s'%e  
            return
        X2 = make_image(redband,greenband,blueband,rows,cols,enhance)    
        f, ax = plt.subplots(1,2,figsize=(20,10))
        ax[0].imshow(X1)
        ax[0].set_title(filename1)
        ax[1].imshow(X2)
        ax[1].set_title(filename2)
    else:
        f, ax = plt.subplots( figsize=(10,10))
        ax.imshow(X1)
        ax.set_title(filename1) 
    plt.show()
                      

def main():
    usage = '''Usage: python %s [-c] [-C] [-f filename1] [-F filename2] [-p posf] [P posF [-d dimsf] [-D dimsF]\n
                                        [-e enhancementf] [-E enhancementF\n
            if -f is not specified it will be queried\n
            use -c or -C for classification image\n 
            RGB bandPositions and spatialDimensions are lists, e.g., -p [1,4,3] -d [0,0,400,400] \n
            enhancements: 1=linear255 2=linear 3=linear2pc 4=equalization\n'''%sys.argv[0]
    options,args = getopt.getopt(sys.argv[1:],'hcCf:F:p:P:d:D:e:E:')
    filename1 = None
    filename2 = None
    dims = None
    rgb = None
    DIMS = None
    RGB = None
    enhance = None   
    ENHANCE = None
    cls = False
    CLS = False
    for option, value in options: 
        if option == '-h':
            print usage
            return 
        elif option == '-f':
            filename1 = value
        elif option == '-F':
            filename2 = value    
        elif option == '-p':
            rgb = tuple(eval(value))
        elif option == '-P':
            RGB = tuple(eval(value))    
        elif option == '-d':
            dims = eval(value) 
        elif option == '-D':
            DIMS = eval(value)    
        elif option == '-e':
            enhance = eval(value)  
        elif option == '-E':
            ENHANCE = eval(value)    
        elif option == '-c':
            cls = True  
        elif option == '-C':
            CLS = True                
                    
    dispms(filename1,filename2,dims,DIMS,rgb,RGB,enhance,ENHANCE,cls,CLS)

if __name__ == '__main__':
    main()