FROM     debian:jessie
MAINTAINER Mort Canty "mort.canty@gmail.com"
ENV     REFRESHED_AT 2014-12-31
RUN apt-get update && apt-get install -y \
    python \
    build-essential \
    make \
    gcc \
    pandoc \
    dos2unix \
    python-dev \
    python-pygments \
    python-pip 

# ipython notebook
RUN     pip install "ipython[notebook]"

# install python environment for crc scripts
RUN     apt-get -y install python-numpy python-scipy python-gdal python-matplotlib gdal-bin

# packages imported by auxil package (but not used)
RUN     apt-get -y install python-tk
RUN     apt-get -y install python-mlpy

# setup the prov_means library
COPY    prov_means.c /crc/prov_means.c
WORKDIR /crc
RUN     gcc -shared -Wall -g -o libprov_means.so -fPIC prov_means.c
RUN     cp libprov_means.so /usr/lib/libprov_means.so

# install auxil package
ADD     auxil-1.1 /auxil-1.1
WORKDIR /auxil-1.1
RUN     python setup.py install   
WORKDIR /crc 

# ipython notebook startup script
ADD     notebook.sh /
RUN     chmod u+x /notebook.sh
RUN     dos2unix /notebook.sh

EXPOSE 8888

# add the Python scripts and set the startup command
ENV     SCRIPTS_CHANGED 2015-01-03c
COPY    iMad.py /crc/iMad.py 
COPY    radcal.py /crc/radcal.py
COPY    em.py /crc/em.py
COPY    register.py /crc/register.py
COPY    atwt.py /crc/atwt.py
COPY    dwt.py /crc/dwt.py
COPY    normalize /crc/normalize
COPY    c-correction.sh /crc/c-correction.sh
COPY    c_corr.py /crc/c_corr.py
COPY    dispms.py /crc/dispms.py
COPY    pca.py /crc/pca.py
ADD     tutorial /crc/tutorial
CMD     ["/notebook.sh"]

