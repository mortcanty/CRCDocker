#!/usr/bin/env python
#******************************************************************************
#  Name:     radcal.py
#  Purpose:  Automatic radiometric normalization
#  Usage:             
#       python radcal.py  [-p 'bandPositions' -d 'spatialDimensions' -t NoChangeProbThresh] imadFile [FullSceneFile] 
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

import sys, os, getopt
from numpy import *
from scipy import stats
from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly, GDT_Float32
from auxil.auxil import orthoregress

 
def main():
    usage = '''
Usage: 
--------------------------------------------------------
python %s  [-p "bandPositions"] [-d "spatialDimensions"] 
[-t no-change prob threshold] imadFile [fullSceneFile]' 
--------------------------------------------------------
bandPositions and spatialDimensions are quoted lists, 
e.g., -p "[4,5,6]" -d "[0,0,400,400]"

SpatialDimensions MUST match those of imadFile
spectral dimension of fullSceneFile, if present,
MUST match those of target and reference images
--------------------------------------------------------
imadFile is of form path/MAD[filename1-filename2].ext and
the output file is named 

            path/filename2_norm.ext.

That is, it is assumed that filename1 is reference and
filename2 is target and the output retains the format
of the imadFile. A similar convention is used to
name the normalized full scene, if present:

         fullSceneFile_norm.ext

Note that, for ENVI format, ext is the empty string.
-------------------------------------------------------'''%sys.argv[0]

    options, args = getopt.getopt(sys.argv[1:],'hp:d:t:')
    pos = None
    dims = None
    ncpThresh = 0.95  
    fsfn = None          
    for option, value in options:
        if option == '-h':
            print usage
            sys.exit(1) 
        elif option == '-p':
            pos = eval(value)
        elif option == '-d':
            dims = eval(value) 
        elif option == '-t':
            ncpThresh = value    
    if (len(args) != 1) and (len(args) != 2):
        print 'Incorrect number of arguments'
        print usage
        sys.exit(1)
    imadfn = args[0]
    if len(args) == 2:
        fsfn = args[1]                                    
        path = os.path.dirname(fsfn)
        basename = os.path.basename(fsfn)
        root, ext = os.path.splitext(basename)
        fsoutfn = path+'/'+root+'_norm'+ext
    path = os.path.dirname(imadfn)
    basename = os.path.basename(imadfn)
    root, ext = os.path.splitext(basename)
    b = root.find('[')
    e = root.find(']')
    referencefn, targetfn = root[b+1:e].split('-')
    referencefn = path+'/'+referencefn
    root, ext = os.path.splitext(targetfn)
    targetfn = path+'/'+targetfn
    outfn = path+'/'+root+'_norm'+ext
    imadDataset = gdal.Open(imadfn,GA_ReadOnly)    
    imadbands = imadDataset.RasterCount 
    cols = imadDataset.RasterXSize
    rows = imadDataset.RasterYSize
    chisqr = imadDataset.GetRasterBand(imadbands).ReadAsArray(0,0,cols,rows).ravel()
    ncp = 1 - stats.chi2.cdf(chisqr,[imadbands-1])
    idx = where(ncp>ncpThresh)
    print '========================================='
    print '             RADCAL'
    print '========================================='
    print 'reference: '+referencefn
    print 'target   : '+targetfn   
    print 'no-change probability threshold: '+str(ncpThresh)
    print 'no-change pixels: '+str(len(idx[0]))
    print 'slope         intercept      correlation'   
    referenceDataset = gdal.Open(referencefn,GA_ReadOnly)     
    targetDataset = gdal.Open(targetfn,GA_ReadOnly)   
    if pos is None:
        pos = range(1,referenceDataset.RasterCount+1)      
    if dims is None:
        x0 = 0; y0 = 0
    else:
        x0,y0,cols,rows = dims                  
    driver = targetDataset.GetDriver()    
    outDataset = driver.Create(outfn,cols,rows,len(pos),GDT_Float32)
    projection = imadDataset.GetProjection()
    geotransform = imadDataset.GetGeoTransform()
    if geotransform is not None:
        outDataset.SetGeoTransform(geotransform)
    if projection is not None:
        outDataset.SetProjection(projection)    
    aa = []
    bb = []  
    for k in pos:
        x = referenceDataset.GetRasterBand(k).ReadAsArray(x0,y0,cols,rows).astype(float).ravel()
        y = targetDataset.GetRasterBand(k).ReadAsArray(x0,y0,cols,rows).astype(float).ravel()
        b,a,R = orthoregress(y[idx],x[idx])
        print b,a,R
        aa.append(a)
        bb.append(b)     
        outBand = outDataset.GetRasterBand(k)
        outBand.WriteArray(resize(a+b*y,(rows,cols)),0,0) 
        outBand.FlushCache()
    outDataset = None
    print 'result written to: '+outfn 
    if fsfn is not None:
        print 'normalizing '+fsfn+'...'
        fsDataset = gdal.Open(fsfn,GA_ReadOnly)
        cols = fsDataset.RasterXSize
        rows = fsDataset.RasterYSize    
        bands = fsDataset.RasterCount
        driver = fsDataset.GetDriver()
        outDataset = driver.Create(fsoutfn,cols,rows,bands,GDT_Float32)
        projection = fsDataset.GetProjection()
        geotransform = fsDataset.GetGeoTransform()
        if geotransform is not None:
            outDataset.SetGeoTransform(geotransform)
        if projection is not None:
            outDataset.SetProjection(projection) 
        for k in pos:
            inBand = fsDataset.GetRasterBand(k)
            outBand = outDataset.GetRasterBand(k)
            for i in range(rows):
                y = inBand.ReadAsArray(0,i,cols,1)
                outBand.WriteArray(aa[k-1]+bb[k-1]*y,0,i) 
            outBand.FlushCache()       
        outDataset = None    
        print 'result written to: '+fsoutfn
    print '-------done-----------------------------'
    
if __name__ == '__main__':
    main()        