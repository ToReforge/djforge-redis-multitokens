#!/usr/bin/env python

from setuptools import setup


setup(
    name='djforge_redis_multitokens',
    version='0.0.3',
    packages=['djforge_redis_multitokens'],
    license='MIT',
    author='Mikaeil Orfanian',
    description='Django REST Framework user auth using multiple tokens stored in Redis',
    author_email='it@toreforge.com',
    install_requires=['passlib', 'djangorestframework', 'django'],
    include_package_data=True,
    url='https://github.com/ToReforge/djforge-redis-multitokens/archive/0.0.2.tar.gz',
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
