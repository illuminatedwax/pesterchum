#!/bin/bash
#
# Lexi's ./configure script
#
echo "Lexi's lazy configuration. This is not an official configure script. Press enter to confirm this."
read confirm
if [ ! -d python ]
then
    echo "Rename your python folder to python."
    exit 1
fi
cd python
if [! -d python ]
then
    echo "Rename your python folder to python."
    exit 1
fi
if [ -e makefile ]
then
    make clean
fi
./configure --enable-framework --enable-universalsdk=/ --with-universal-archs=intel MACOSX_DEPLOYMENT_TARGET=10.6 
echo "---~ Done ~---"
