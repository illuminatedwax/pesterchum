#!/bin/bash
#
# Lexi's Configurations
#

echo "Lexi's lazy configuration. This is not an official configure script. Press enter to confirm this."
read confirm
if [ ! -d sip ]
then
    echo "Rename your sip folder to sip."
    exit 1
fi
cd sip
if [ -e makefile ]
then
    make clean
fi
python configure.py --arch=i386 --arch=x86_64 \
                    --universal --deployment-target=10.5 \
                    --destdir=/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/site-packages/
echo "---~ Done ~---"
