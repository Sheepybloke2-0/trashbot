#!/bin/sh
mkdir deps
if [ $# != 1 ]
then
    echo "No parameters specified! Must have system specified: pi or laptop."
    exit 0
fi
if [ $1 = "pi" ]
then
    ARCH=armv7l
else
    ARCH=x86_64
fi

if [ ! -f "deps/precise-engine.tar.gz" ]
then
    wget -P deps https://github.com/MycroftAI/precise-data/raw/dist/$ARCH/precise-engine.tar.gz
fi
if [ ! -d "deps/precise-engine" ]
then 
    tar xvf deps/precise-engine.tar.gz -C deps/
fi

sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev\
portaudio19-dev libopenblas-dev libhdf5-dev 
pip install precise-runner
