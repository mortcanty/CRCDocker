#!/usr/bin/env python
#******************************************************************************
#  Name:     register.py
#  Purpose:  Perfrom image-image registration in frequency domain
#  Usage:             
#    python register.py 
#
#  Copyright (c) 2013, Mort Canty
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

from auxil.auxil import similarity
import os, sys, getopt, time
import numpy as np
from osgeo import gdal
import scipy.ndimage.interpolation as ndii
from osgeo.gdalconst import GA_ReadOnly, GDT_Float32
  
def main(): 
    usage = '''
Usage:
------------------------------------------------
python %s [-h] [-b warpband] refname warpfname  

Choose a reference image, the image to be warped and, optionally,
the band to be used for warping (default band 1). 

The reference image should be smaller than the warp image 
(i.e., the warp image should overlap the reference image completely) 
and its upper left corner should be near that of the warp image:
----------------------
|   warp image
|
|  --------------------
|  |
|  |  reference image
|  |   

The warped image (warpfile_warp) will be trimmed to the spatial 
dimensions of the reference image.
------------------------------------------------''' %sys.argv[0]
    options, args = getopt.getopt(sys.argv[1:],'hb:')  
    warpband = 1
    for option, value in options:
        if option == '-h':
            print usage
            sys.exit(1)   
        elif option == '-b':
            warpband = eval(value)       
    if len(args) != 2:
        print 'Incorrect number of arguments'
        print usage
        sys.exit(1)            
    gdal.AllRegister()    
    fn1 = args[0]  # reference
    fn2 = args[1]  # warp           
    print '========================='
    print '       Register'
    print '========================='
    print time.asctime()     
    print 'reference image: '+fn1
    print 'warp image: '+fn2     
    print 'warp band: %i'%warpband                 

    path2 = os.path.dirname(fn2)
    basename2 = os.path.basename(fn2)
    root2, ext2 = os.path.splitext(basename2)
    outfn = path2+basename2+'_warp'+ext2
    inDataset1 = gdal.Open(fn1,GA_ReadOnly)     
    inDataset2 = gdal.Open(fn2,GA_ReadOnly)
    cols1 = inDataset1.RasterXSize
    rows1 = inDataset1.RasterYSize    
    bands1 = inDataset1.RasterCount
    cols2 = inDataset2.RasterXSize
    rows2 = inDataset2.RasterYSize    
    bands2 = inDataset2.RasterCount    
    
    band = inDataset1.GetRasterBand(warpband)
    refband = band.ReadAsArray(0,0,cols1,rows1).astype(float)
    warpimg = np.zeros((bands2,rows2,cols2))                                  
    for k in range(bands2):
        band = inDataset2.GetRasterBand(k+1)
        warpimg[k,:,:]=band.ReadAsArray(0,0,cols2,rows2).astype(float)
    outdriver = inDataset2.GetDriver()    
    inDataset2 = None
#  padded warp image            
    warpimg1 = np.zeros((bands2, rows2 + 100, cols2 + 100), dtype=np.float32)
    warpimg1[:,0:rows2,0:cols2] = warpimg
#  similarity transform parameters for reference band number            
    scale, angle, shift = similarity(refband, warpimg1[warpband-1,:,:])
#  warp  the image
    outimg = np.zeros((bands2,rows1,cols1),dtype=np.float32)  
    for k in range(bands1): 
        bn1 = np.nan_to_num(warpimg1[k, :, :])                  
        bn2 = ndii.zoom(bn1, 1.0 / scale)
        bn2 = ndii.rotate(bn2, angle)
        bn2 = ndii.shift(bn2, shift)
        outimg[k, :, :] = bn2[0:rows1, 0:cols1] 
    
    outDataset = outdriver.Create(outfn,cols1,rows1,bands2,GDT_Float32)
    projection = inDataset1.GetProjection()
    geotransform = inDataset1.GetGeoTransform()
    if geotransform is not None:
        outDataset.SetGeoTransform(geotransform)
    if projection is not None:
        outDataset.SetProjection(projection)        
    for k in range(bands2):        
        outBand = outDataset.GetRasterBand(k+1)
        outBand.WriteArray(outimg[k,:,:],0,0) 
        outBand.FlushCache() 
    inDataset1 = None
    outDataset = None    
    print 'Warped image written to: %s'%outfn

if __name__ == '__main__':
    main()    