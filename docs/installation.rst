Installation
============

Use pip to install the module:

.. code-block:: sh

    $ pip install django-balancer

Then, add the desired router to your DATABASE_ROUTERS setting::

    DATABASE_ROUTERS = ['balancer.routers.WeightedRandomRouter']

Finally, add any configuration settings needed for the router chosen::

    DATABASE_POOL = {
        'default': 2,
        'db02': 1,
        'db03': 1,
    }
