Django-Balancer
===============

.. image:: https://badge.fury.io/py/django-balancer.png
    :alt: The PyPI package
    :target: http://badge.fury.io/py/django-balancer

.. image:: https://img.shields.io/pypi/dw/django-balancer.svg
    :alt: PyPI download statistics
    :target: https://pypi.python.org/pypi/django-balancer

.. image:: https://travis-ci.org/michaelhelmick/django-balancer.png
  :target: https://travis-ci.org/michaelhelmick/django-balancer

.. image:: https://coveralls.io/repos/michaelhelmick/django-balancer/badge.svg?branch=master
  :target: https://coveralls.io/r/michaelhelmick/django-balancer?branch=master

A set of tools for using Django's multi-db feature to balance database requests
between multiple replicated databases.  It currently provides some basic
routers for using weighted random selection or round robin selection with a
pool of databases, following a master/slave layout where the slaves are
read-only copies of master, and pinning reads to master for a user after that
user completes a write.

Since everything is implemented using base classes and mixins, this also serves
as a construction kit for creating your own more complex routers.  Feel free to
contribute routers, and I'll be happy to incorporate them into the project.

Install
-------

Install django-balancer via `pip <http://www.pip-installer.org/>`_

.. code-block:: bash

    $ pip install django-balancer

or, with `easy_install <http://pypi.python.org/pypi/setuptools>`_

.. code-block:: bash

    $ easy_install django-balancer

But, hey... `that's up to you <http://www.pip-installer.org/en/latest/other-tools.html#pip-compared-to-easy-install>`_.


Documentation
-------------

https://django-balancer.readthedocs.org/en/latest/
