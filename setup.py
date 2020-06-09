import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

setup(
    name='jirasession',
    version='0.2.4',
    packages=find_packages(),
    include_package_data=True,
    description='A light weight library to interact with the Jira API',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://www.github.com/tannerburns/jirasession',
    author='Tanner Burns',
    author_email='tjburns102@gmail.com',
    install_requires=[
        'requests'
    ],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
    ],
)