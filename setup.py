# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name = 'pyswrve',
    version = '0.1',
    license='MIT License',
    
    author = 'Oleg Kozlov (xxblx)',
    author_email = 'olkozlov@playrix.com',
    
    description = 'Unofficial Python wrapper for Swrve Export API',
    
    requires = ['requests', 'psycopg2'],

    packages = ['pyswrve'],
    
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='swrve swrve.com export api wrapper'
)
