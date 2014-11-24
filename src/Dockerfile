FROM     debian:jessie
MAINTAINER Mort Canty "mort.canty@gmail.com"
ENV     REFRESHED_AT 2014-09-29
RUN apt-get update && apt-get install -y \
    python \
    build-essential \
    make \
    gcc \
    python-dev \
    python-pip

# install python environment for iMad
RUN     apt-get -y install python-numpy python-scipy python-gdal

# packages imported by auxil package (but not used)
RUN     apt-get -y install python-tk
RUN     apt-get -y install python-mlpy

# setup the prov_means library
COPY    prov_means.c /crc/prov_means.c
WORKDIR /crc
RUN     gcc -shared -Wall -g -o libprov_means.so -fPIC prov_means.c
RUN     cp libprov_means.so /usr/lib/libprov_means.so

# install auxil package
ADD     auxil-1.1 /crc/auxil-1.1
WORKDIR /crc/auxil-1.1
RUN     python setup.py install   
WORKDIR /crc 

# add the Python scripts and set the startup command
ENV     SCRIPTS_CHANGED 2014-11-24
COPY    iMad.py /crc/iMad.py 
COPY    radcal.py /crc/radcal.py
COPY    em.py /crc/em.py
COPY    register.py /crc/register.py
COPY    atwt.py /crc/atwt.py
COPY    dwt.py /crc/dwt.py
COPY    normalize /crc/normalize
CMD     ["/bin/bash"]
