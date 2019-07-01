import setuptools
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='eagle200_reader',
    version='0.1.2',
    description='A program to read from an Rainforest Eagle-200 on the local network',
    long_description=long_description,
    url='https://github.com/gtdiehl/eagle200_reader',
    packages=setuptools.find_packages(),
)