# -*- coding: utf-8 -*-

from distutils.core import setup

from pyswrve import __version__

setup(
    name='pyswrve',
    version=__version__,
    license='MIT License',
    url='https://github.com/xxblx/pyswrve',

    author='Oleg Kozlov',
    author_email='xxblx@posteo.org',

    description='Unofficial Python wrapper for Swrve Non-Client APIs',
    long_description="""pyswrve is an unofficial Python wrapper for
Swrve Non-Client APIs: Export API (ready) and Items API (todo).""",

    requires=['requests'],
    platforms=['any'],
    packages=['pyswrve'],

    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='swrve api wrapper'
)
