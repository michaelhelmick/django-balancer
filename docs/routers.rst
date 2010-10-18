Routers
=======

WeightedRandomRouter
********************

This router randomly selects from a weighted pool of databases for both reads
and writes.  This would be useful for replication configurations where all
nodes act as masters, but you'd like some nodes to get more traffic than
others.

Settings Needed
---------------

``DATABASE_POOL``
~~~~~~~~~~~~~~~~~

A dict mapping the databases that should be included in the pool to to their
weights.

Example::

    DATABASE_POOL = {
        'default': 2,
        'db02': 1,
        'db03': 1,
    }

WeightedMasterSlaveRouter
*************************

This router allows you to use the database pool for reads, but only the
database you designate as master for writes.  This is useful for master/slave
configurations.  If you don't include the master database in the pool, it will
only be used for writes.

Settings Needed
---------------

``DATABASE_POOL``
~~~~~~~~~~~~~~~~~

A dict mapping the databases that should be used for reads to their weights.

``MASTER_DATABASE``
~~~~~~~~~~~~~~~~~~~

The database that should be used for all writes.

Example::

    MASTER_DATABASE = 'default'
