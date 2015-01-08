#!/usr/bin/env python
#******************************************************************************
#  Name:     classify.py
#  Purpose:  supervised classification of multispectral images
#  Usage:             
#    python classify.py
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
import auxil.supervisedclass as sc
import gdal, ogr, osr, os, time, sys, getopt
from osgeo.gdalconst import GA_ReadOnly, GDT_Byte
from shapely.geometry import asPolygon, MultiPoint
import matplotlib.pyplot as plt
import shapely.wkt  
import numpy as np
 
def main():    
    usage = '''
Usage: 
---------------------------------------------------------
python %s  [-p bandPositions] [- c classifier] [-L number of hidden neurons]   
[-P generate class probabilities image] filename trainShapefile

bandPositions is a list, e.g., -p [1,2,4]  

classifier 1=MaxLike
           2=NNet(backprop)
           3=NNet(congrad)
           4=SVM

If the input file is named 

         path/filenbasename.ext then

The output classification file is named 

         path/filebasename_class.ext

the class probabilities output file is named

         path/filebasename_classprobs.ext
         
and the test results file is named

         path/filebasename_<classifier>.tst
--------------------------------------------------------''' %sys.argv[0]
    options, args = getopt.getopt(sys.argv[1:],'hnPp:c:L:')
    pos = None
    probs = False   
    L = 8
    trainalg = 1
    graphics = True
    for option, value in options:
        if option == '-h':
            print usage
            return
        elif option == '-p':
            pos = eval(value)
        elif option == '-n':
            graphics = False            
        elif option == '-c':
            trainalg = eval(value)
        elif option == '-L':
            L = eval(value)    
        elif option == '-P':
            probs = True                              
    if len(args) != 2: 
        print 'Incorrect number of arguments'
        print usage
        sys.exit(1)      
    if trainalg == 1:
        algorithm = 'MaxLike'
    elif trainalg == 2:
        algorithm = 'NNet(Backprop)'
    elif trainalg ==3:
        algorithm =  'NNet(Congrad)'
    else:
        algorithm = 'SVM'              
    infile = args[0]  
    trnfile = args[1]      
    gdal.AllRegister() 
    if infile:                   
        inDataset = gdal.Open(infile,GA_ReadOnly)
        cols = inDataset.RasterXSize
        rows = inDataset.RasterYSize    
        bands = inDataset.RasterCount
        projection = inDataset.GetProjection()
        geotransform = inDataset.GetGeoTransform()
        if geotransform is not None:
            gt = list(geotransform) 
        else:
            print 'No geotransform available'
            return       
        imsr = osr.SpatialReference()  
        imsr.ImportFromWkt(projection)    
    else:
        return  
    if pos is None: 
        pos = range(1,bands+1)
    N = len(pos)    
    rasterBands = [] 
    for b in pos:
        rasterBands.append(inDataset.GetRasterBand(b))     
#  output files
    path = os.path.dirname(infile)
    basename = os.path.basename(infile)
    root, ext = os.path.splitext(basename)
    outfile = '%s/%s_class%s'%(path,root,ext)  
    tstfile = '%s/%s_%s.tst'%(path,root,algorithm)            
    if (trainalg in (2,3,4)) and probs:
#      class probabilities file
        probfile = '%s/%s_classprobs%s'%(path,root,ext) 
    else:
        probfile = None        
#  training data        
    trnDriver = ogr.GetDriverByName('ESRI Shapefile')
    trnDatasource = trnDriver.Open(trnfile,0)
    trnLayer = trnDatasource.GetLayer() 
    trnsr = trnLayer.GetSpatialRef()             
#  coordinate transformation from training to image projection   
    ct = osr.CoordinateTransformation(trnsr,imsr) 
#  number of classes    
    feature = trnLayer.GetNextFeature() 
    while feature:
        classid = feature.GetField('CLASS_ID')
        feature = trnLayer.GetNextFeature() 
    trnLayer.ResetReading()    
    K = int(classid)+1       
#  es kann losgehen    
    print '========================='
    print 'supervised classification'
    print '========================='
    print time.asctime()    
    print 'image:    '+infile
    print 'training: '+trnfile  
    print algorithm             
#  loop through the polygons    
    Gs = [] # train observations
    ls = [] # class labels
    classnames = '{unclassified'
    classids = set()
    print 'reading training data...'
    for i in range(trnLayer.GetFeatureCount()):
        feature = trnLayer.GetFeature(i)
        classid = feature.GetField('CLASS_ID')
        classname  = feature.GetField('CLASS_NAME')
        if classid not in classids:
            classnames += ',   '+ classname
        classids = classids | set(classid)     
#      label for this ROI           
        l = [0 for i in range(K)]
        l[int(classid)] = 1.0
        polygon = feature.GetGeometryRef()
#      transform to same projection as image        
        polygon.Transform(ct)  
#      convert to a Shapely object            
        poly = shapely.wkt.loads(polygon.ExportToWkt())
#      transform the boundary to pixel coords in numpy        
        bdry = np.array(poly.boundary) 
        bdry[:,0] = bdry[:,0]-gt[0]
        bdry[:,1] = bdry[:,1]-gt[3]
        GT = np.mat([[gt[1],gt[2]],[gt[4],gt[5]]])
        bdry = bdry*np.linalg.inv(GT) 
#      polygon in pixel coords        
        polygon1 = asPolygon(bdry)
#      raster over the bounding rectangle        
        minx,miny,maxx,maxy = map(int,list(polygon1.bounds))  
        pts = [] 
        for i in range(minx,maxx+1):
            for j in range(miny,maxy+1): 
                pts.append((i,j))             
        multipt =  MultiPoint(pts)   
#      intersection as list              
        intersection = np.array(multipt.intersection(polygon1),dtype=np.int).tolist()
#      cut out the bounded image cube               
        cube = np.zeros((maxy-miny+1,maxx-minx+1,len(rasterBands)))
        k=0
        for band in rasterBands:
            cube[:,:,k] = band.ReadAsArray(minx,miny,maxx-minx+1,maxy-miny+1)
            k += 1
#      get the training vectors
        for (x,y) in intersection:         
            Gs.append(cube[y-miny,x-minx,:])
            ls.append(l)   
        polygon = None
        polygon1 = None            
        feature.Destroy()  
    trnDatasource.Destroy() 
    classnames += '}'
    m = len(ls)       
    print str(m) + ' training pixel vectors were read in' 
    Gs = np.array(Gs) 
    ls = np.array(ls)
#  stretch the pixel vectors to [-1,1] for ffn
    maxx = np.max(Gs,0)
    minx = np.min(Gs,0)
    for j in range(N):
        Gs[:,j] = 2*(Gs[:,j]-minx[j])/(maxx[j]-minx[j]) - 1.0 
#  random permutation of training data
    idx = np.random.permutation(m)
    Gs = Gs[idx,:] 
    ls = ls[idx,:]     
#  train on 2/3 training examples         
    Gstrn = Gs[0:2*m//3,:]
    lstrn = ls[0:2*m//3,:] 
    Gstst = Gs[2*m//3:,:]  
    lstst = ls[2*m//3:,:]               
#  setup output datasets 
    driver = inDataset.GetDriver() 
    outDataset = driver.Create(outfile,cols,rows,1,GDT_Byte) 
    projection = inDataset.GetProjection()
    geotransform = inDataset.GetGeoTransform()
    if geotransform is not None:
        outDataset.SetGeoTransform(tuple(gt))
    if projection is not None:
        outDataset.SetProjection(projection) 
    outBand = outDataset.GetRasterBand(1) 
    if probfile:   
        probDataset = driver.Create(probfile,cols,rows,K,GDT_Byte) 
        if geotransform is not None:
            probDataset.SetGeoTransform(tuple(gt))
        if projection is not None:
            probDataset.SetProjection(projection)  
        probBands = [] 
        for k in range(K):
            probBands.append(probDataset.GetRasterBand(k+1))         
#  initialize classifier  
    if   trainalg == 1:
        classifier = sc.Maxlike(Gstrn,lstrn)
    elif trainalg == 2:
        classifier = sc.Ffnbp(Gstrn,lstrn,L)
    elif trainalg == 3:
        classifier = sc.Ffncg(Gstrn,lstrn,L)
    elif trainalg == 4:
        classifier = sc.Svm(Gstrn,lstrn)         
#  train it            
    print 'training on %i pixel vectors...' % np.shape(Gstrn)[0]
    start = time.time()
    result = classifier.train()
    print 'elapsed time %s' %str(time.time()-start) 
    if result:
        if (trainalg in [2,3]) and graphics:
            cost = np.log10(result)  
            ymax = np.max(cost)
            ymin = np.min(cost) 
            xmax = len(cost)      
            plt.plot(range(xmax),cost,'k')
            plt.axis([0,xmax,ymin-1,ymax])
            plt.title('Log(Cross entropy)')
            plt.xlabel('Epoch')              
#      classify the image           
        print 'classifying...'
        start = time.time()
        tile = np.zeros((cols,N),dtype=np.float32)    
        for row in range(rows):
            for j in range(N):
                tile[:,j] = rasterBands[j].ReadAsArray(0,row,cols,1)
                tile[:,j] = 2*(tile[:,j]-minx[j])/(maxx[j]-minx[j]) - 1.0               
            cls, Ms = classifier.classify(tile)  
            outBand.WriteArray(np.reshape(cls,(1,cols)),0,row)
            if probfile:
                Ms = np.byte(Ms*255)
                for k in range(K):
                    probBands[k].WriteArray(np.reshape(Ms[k,:],(1,cols)),0,row)
        outBand.FlushCache()
        print 'elapsed time %s' %str(time.time()-start)
        outDataset = None
        inDataset = None      
        if probfile:
            for probBand in probBands:
                probBand.FlushCache() 
            probDataset = None
            print 'class probabilities written to: %s'%probfile   
        K =  lstrn.shape[1]+1                     
        print 'thematic map written to: %s'%outfile
        if trainalg in [2,3]:
            plt.show()
        if tstfile:
            with open(tstfile,'w') as f:               
                print >>f, algorithm +'test results for %s'%infile
                print >>f, time.asctime()
                print >>f, 'Classification image: %s'%outfile
                print >>f, 'Class probabilities image: %s'%probfile
                print >>f, lstst.shape[0],lstst.shape[1]
                classes, _ = classifier.classify(Gstst)
                labels = np.argmax(lstst,axis=1)+1
                for i in range(len(classes)):
                    print >>f, classes[i], labels[i]              
                f.close()
                print 'test results written to: %s'%tstfile
        print 'done'
    else:
        print 'an error occured' 
        return 
   
if __name__ == '__main__':
    main()