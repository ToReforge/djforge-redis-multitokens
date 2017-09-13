#!/usr/bin/env python

from setuptools import setup


with open('README.rst', 'r') as f:
    readme = f.read()

setup(
    name='djforge_redis_multitokens',
    version='0.0.4',
    packages=['djforge_redis_multitokens'],
    license='MIT',
    author='ToReforge',
    description='Django REST Framework user auth using multiple tokens stored in Redis',
    long_description=readme,
    author_email='it@toreforge.com',
    install_requires=['passlib', 'djangorestframework', 'django'],
    include_package_data=True,
    url='https://github.com/ToReforge/djforge-redis-multitokens',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ]
)
