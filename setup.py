from distutils.core import setup

VERSION = __import__('balancer').__version__

try:
    long_description = open('README', 'rt').read()
except IOError:
    long_description = ''

description = "A set of tools for using Django's multi-db feature to balance "
description += "database requests"

setup(
    name='django-balancer',
    version=VERSION,
    description=description,
    long_description = long_description,
    author='Brandon Konkle',
    author_email='brandon@brandonkonkle.com',
    license='License :: OSI Approved :: BSD License',
    url='http://github.com/bkonkle/django-balancer',
    packages=['balancer'],
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
    ]
)
