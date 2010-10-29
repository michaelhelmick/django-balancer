Settings
========

.. _database-pool:

``DATABASE_POOL``
*****************

Can be either a list of database names to include in the pool, or a dict
mapping the databases to their weights.

Example::

    DATABASE_POOL = {
        'default': 2,
        'db02': 1,
        'db03': 1,
    }

.. _master-database:

``MASTER_DATABASE``
*******************

The database that should be used for all writes.  Expects a string.

.. _master-pinning-key:

``MASTER_PINNING_KEY``
**********************

The name of the session variable or cookie used by the pinning middleware.
Expects a string.

Defaults to: ``'master_db_pinned'``

.. _master-pinning-seconds:

``MASTER_PINNING_SECONDS``
**************************

The number of seconds to direct reads to the master database after a write.
Expects an integer.

Defaults to: ``5``