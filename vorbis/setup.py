# setup.py

from distutils.core import setup, Extension

setup(
    name="PyExVorbis",
    version="0.0.1",
    description="Python Vorbis Module",
    author="Ignatius Kunjumon",
    author_email="ignatius.kunjumon@gmail.com",
    maintainer="Vigith Maurice <www.vigith.com>",
    maintainer_email="vigith@gmail.com",
    url="http://xiph.org/vorbis/",
    license="GPL",
    ext_modules=[Extension("PyExVorbis", ["pyEx_vorbis.c"],
                        library_dirs=["/usr/lib/" , "/opt/local/include/"],
                        include_dirs=["/usr/include/" , "/opt/local/include/"],
                        libraries=['ogg', 'vorbisenc', 'vorbis'])]
)
