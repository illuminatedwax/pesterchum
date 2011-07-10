#!/bin/bash
echo "Lexi's lazy configuration. This is not an official configure script. Press enter to confirm this."
read confirm
if [ ! -d pyqt4 ]
then
    echo "Rename your pyqt4 folder to pyqt4."
    exit 1
fi
cd pyqt4
if [ -e makefile ]
then
    make clean
fi
python configure.py \
    --confirm-license \
    --use-arch=i386 \
    --use-arch=x86_64 \
    --destdir=/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/site-packages \
    --verbose
echo "---~ Done ~---"
