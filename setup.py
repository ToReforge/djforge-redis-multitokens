#!/usr/bin/env python

from setuptools import setup


with open('README.md', 'r') as f:
    readme = f.read()


setup(
    name='djforge_redis_multitokens',
    version='0.1.0',
    packages=['djforge_redis_multitokens'],
    license='MIT',
    author='Mikaeil Orfanian',
    description='Django REST Framework user auth using multiple tokens stored in Redis',
    author_email='mokt@outlook.com',
    long_description=readme,
    install_requires=['passlib', 'djangorestframework', 'django'],
    include_package_data=True,
    url='https://github.com/ToReforge/djforge_redis_multitokens',
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
