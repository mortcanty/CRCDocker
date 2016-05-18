# x86 architecture 
FROM     debian:jessie  
           
# arm (raspberry pi) architecture       
#FROM     resin/rpi-raspbian 

MAINTAINER Mort Canty "mort.canty@gmail.com"
ENV     REFRESHED_AT 2015-12-26
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

# enable parallel computing
RUN     pip install ipyparallel
RUN     jupyter notebook --generate-config
RUN     sed -i "/# Configuration file for jupyter-notebook./a  \ 
                c.NotebookApp.server_extensions.append('ipyparallel.nbextension')" \
            /root/.jupyter/jupyter_notebook_config.py

# install python environment for crc scripts
RUN     apt-get install -y python-numpy python-scipy \
         python-gdal python-matplotlib libgdal-dev gdal-bin python-shapely \
         python-opencv

# install *latest* mlpy (with MaximumLikelihoodC and LibSvm)
RUN     apt-get install -y libgsl0-dev
ADD     mlpy-3.5.0 /mlpy-3.5.0
WORKDIR /mlpy-3.5.0
RUN     python setup.py install

# package imported by auxil package (but not used)
RUN     apt-get install -y python-tk 

# setup the prov_means library
COPY    prov_means.c /home/prov_means.c
WORKDIR /home
RUN     gcc -shared -Wall -g -o libprov_means.so -fPIC prov_means.c
RUN     cp libprov_means.so /usr/lib/libprov_means.so

# ipython notebook startup script
ADD     notebook.sh /
RUN     chmod u+x /notebook.sh
RUN     dos2unix /notebook.sh

EXPOSE 8888

# add the Python scripts and set the startup command
ENV     SCRIPTS_CHANGED 2015-12-09
COPY    dist/auxil-1.1.tar.gz /home/auxil-1.1.tar.gz
RUN     tar -xzvf auxil-1.1.tar.gz
WORKDIR /home/auxil-1.1
RUN     python setup.py install  
WORKDIR /home
RUN     rm -rf auxil-1.1
RUN     rm auxil-1.1.tar.gz
COPY    iMad.py /home/iMad.py 
COPY    radcal.py /home/radcal.py
COPY    em.py /home/em.py
COPY    register.py /home/register.py
COPY    atwt.py /home/atwt.py
COPY    dwt.py /home/dwt.py
COPY    canny.py /home/canny.py
COPY    classify.py /home/classify.py
COPY    classify_cv.py /home/classify_cv.py
COPY    ct.py /home/ct.py
COPY    mcnemar.py /home/mcnemar.py
COPY    normalize /home/normalize
COPY    c-correction.sh /home/c-correction.sh
COPY    c_corr.py /home/c_corr.py
COPY    dispms.py /home/dispms.py
COPY    pca.py /home/pca.py
COPY    subset.py /home/subset.py
ADD     tutorial /home/tutorial
WORKDIR /home  
CMD     ["/notebook.sh"]
