from os import path
from setuptools import setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, './readme.md')) as f:
    readme = f.read()

setup(
    name='beets-fileinfo',
    version='0.0.1',
    description='Plugin for the music library manager Beets, to tag sample rates and bit depths.',
    long_description=readme,
    url='https://github.com/Sciencentistguy/BeetsFileInfo',
    download_url='https://github.com/Sciencentistguy/BeetsFileInfo.git',
    author='Jamie Quigley',
    author_email='jamie@quigley.xyz',
    license='GPLv3',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='beets bitdepth',
    packages=['beetsplug'],
    install_requires=['beets>=1.4.3'],
)
