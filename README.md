CRCDocker
=========
Source files for the Docker image mort/crcpython

Command line versions of several Python scripts for the textbook "Image Analysis, Classification and Change Detection in Remote Sensing"

On Ubuntu, for example, pull and run the container with

sudo docker run -i -t -v <my images>:/crc/imagery/ –name=crc mort/crcpython

This maps the host directory <my images> to the container directory /crc/imagery/

In the container, get help with

python iMad.py -h  (IR-MAD algorithm for change detection - Chapter 9)

python radcal.py -h (Automatic relative radiometric normalization -Chapter 9)

python em.py -h (Gaussian mixture clustering with the expectation maximization algorithm -Chapter 8)

python register.py -h (Image-image co-registration in the spatial frequency domain - Chapter 5)

python atwt.py -h (A-trous wavelet transform image fusion - Chapter 5)

python dwt.py -h (Discrete wavelet transform image fusion -Chapter 5)

To carry out automatic radiometric normalization of full scenes (e.g. Landsat TM) run the bash script normalize:

Usage:

./normalize warpbandnumber spectral_subset referencefile targetfile [spatial_subset]

Only the spatial subset is optional.

Spectral and spatial subsets must be lists, e.g., for Landsat images:

./ normalize 4 [1,2,3,4,5,7] reference.tif target.tif [500,500,2000,2000]
