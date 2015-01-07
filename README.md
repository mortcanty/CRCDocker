CRCDocker
=========
Source files for the Docker image mort/crcdocker

Command line versions of several Python scripts for the textbook "Image Analysis, Classification and Change Detection in Remote Sensing"

On Ubuntu, for example, pull and run the container with

sudo docker run -d -p 433:8888 -v my_images:/crc/imagery/ –name=crc mort/crcdocker

This maps the host directory my_images to the container directory /crc/imagery/ and runs the
container as a daemon which is serving iPython notebooks. 

Point your browser to http://localhost:433 to see the iPython notebook home page. 

Open a new notebook and get help with

run dispms.py -h (Display multispectral images - Chapter 1)

run iMad.py -h  (IR-MAD algorithm for change detection - Chapter 9)

run radcal.py -h (Automatic relative radiometric normalization -Chapter 9)

run em.py -h (Gaussian mixture clustering with the expectation maximization algorithm -Chapter 8)

run register.py -h (Image-image co-registration in the spatial frequency domain - Chapter 5)

run atwt.py -h (A-trous wavelet transform image fusion - Chapter 5)

run dwt.py -h (Discrete wavelet transform image fusion -Chapter 5)

To carry out automatic radiometric normalization of full scenes (e.g. Landsat TM) run the bash script normalize:

Usage:

run ./normalize warpbandnumber spectral_subset referencefile targetfile [spatial_subset]

Only the spatial subset is optional.

Spectral and spatial subsets must be lists, e.g., for Landsat images:

!./ normalize 4 [1,2,3,4,5,7] reference.tif target.tif [500,500,2000,2000]
