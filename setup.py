#!/usr/bin/env python
from distutils.core import setup


setup(
    name='Amplify',
    version='0.2.0',
    url='https://github.com/DrMegahertz/amplify',
    license='BSD License',
    author='Marcus Fredriksson',
    author_email='drmegahertz@gmail.com',
    description='Share music with your friends',
    packages=['amplify'],
    package_data={
        'amplify': [
            'static/css/*.css',
            'static/img/*.png',
            'static/js/*.js',
            'static/js/foundation/*.js',
            'static/fonts/*.ttf',
            'templates/*.html',
        ],
    },
    package_dir={
        '': 'src'
    },
    scripts=['amplify'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Communications :: File Sharing',
        'Topic :: Multimedia :: Sound/Audio',
    ],
)
