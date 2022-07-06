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

pip install precise-runner
sudo apt-get install -y portaudio19-dev libopenblas-dev libhdf5-dev 
