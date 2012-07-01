from setuptools import setup

entry_points = {
    'console_scripts': [
        'amplify = amplify.main:main'
    ]
}

setup(
    name='Amplify',
    version='0.0.1',
    url='https://github.com/DrMegahertz/amplify',
    license = 'BSD License',
    author = 'Marcus Fredriksson',
    author_email = 'drmegahertz@gmail.com',
    description = 'Share music with your friends',
    packages = ['amplify'],
    entry_points = entry_points,
    classifiers = [
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
