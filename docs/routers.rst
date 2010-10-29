Routers
=======


RandomRouter
************

Randomly selects from a pool of database for both reads and writes.  Useful for
replication configurations where all nodes act as masters.

Required Settings
-----------------

* :ref:`database-pool`


WeightedRandomRouter
********************

This router applies weighting to the random selection.  This would be useful
for configurations where all nodes act as masters, but you'd like some nodes to
get more traffic than others.

Required Settings
-----------------

* :ref:`database-pool`


RoundRobinRouter
****************

A router that cycles over a pool of databases in order, evenly distributing
the load.  The pool is shuffled upon initialization of the class, to avoid
overloading the master database at startup.

Required Settings
-----------------

* :ref:`database-pool`


WeightedMasterSlaveRouter
*************************

This router allows you to use the database pool for reads, but only the
database you designate as master for writes.  This is useful for master/slave
configurations.  If you don't include the master database in the pool, it will
only be used for writes.  Uses weighted random selection.

Required Settings
-----------------

* :ref:`database-pool`
* :ref:`master-database`


RoundRobinMasterSlaveRouter
***************************

Same as above, but using round robin database selection instead.


PinningWMSRouter
****************

This is a master/slave router that uses weighted random selection and pins
reads to the master for a user after that user has executed a write to the
database.  This is useful for replication configurations where there is a
noticeable amount of lag between a write to master and the propagation of that
data to the slave databases.

To use this router, you also need to use one of the included pinning middleware
classes.  PinningSessionMiddleware uses the Django sessions contrib app, and
PinningCookieMiddleware uses a cookie.

Required Settings
-----------------

* :ref:`database-pool`
* :ref:`master-database`

Optional Settings
-----------------

* :ref:`master-pinning-key`
* :ref:`master-pinning-seconds`


PinningRRMSRouter
*****************

Same as above, but using round robin database selection instead.
