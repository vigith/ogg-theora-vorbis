#!/usr/bin/env python

# setup.py

from distutils.core import setup, Extension
import os

## changed the the library_dirs and include_dirs for MAC
setup(
    name="PyExTheora",
    version="0.0.1",
    description="Python Theora Module",
    author="Ignatius Kunjumon",
    author_email="ignatius.kunjumon@gmail.com",
    maintainer="Vigith Maurice <www.vigith.com>",
    maintainer_email="vigith@gmail.com",
    url="http://www.theora.org/",
    license="GPL",
    ext_modules=[Extension("PyExTheora", ["pyEx_theora.c"],
                           library_dirs=["/usr/lib/" , "/opt/local/include/"],
                           include_dirs=["/usr/include/" , "/opt/local/include/"],
                           libraries=['ogg', 'theora', 'theoraenc', 'theoradec'])]
)

## compiling
## gcc -I /opt/local/include/ -I /opt/local/include/python2.4/ -L /opt/local/lib/libtheora.dylib -L /opt/local/lib/libpython2.4.dylib pyEx_theora.c
