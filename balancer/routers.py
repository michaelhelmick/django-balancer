import bisect
import itertools
import random
import threading
import warnings

from django.conf import settings


_locals = threading.local()


class BasePoolRouter(object):
    """
    A base class for routers that use a pool of databases defined by the
    DATABASE_POOL setting.
    """
    
    def __init__(self):
        if isinstance(settings.DATABASE_POOL, dict):
            self.pool = settings.DATABASE_POOL.keys()
        else:
            self.pool = settings.DATABASE_POOL
    
    def allow_relation(self, obj1, obj2, **hints):
        """Allow any relation between two objects in the pool"""
        if obj1._state.db in self.pool and obj2._state.db in self.pool:
            return True
        return None

    def allow_syncdb(self, db, model):
        """Explicitly put all models on all databases"""
        return True


class RandomRouter(BasePoolRouter):
    """A router that randomly selects from a pool of databases."""

    def db_for_read(self, model, **hints):
        return self.get_random_db()

    def db_for_write(self, model, **hints):
        return self.get_random_db()

    def get_random_db(self):
        return random.choice(self.pool)


class WeightedRandomRouter(RandomRouter):
    """
    A router that randomly selects from a weighted pool of databases, useful
    for replication configurations where all nodes act as masters.
    """

    def __init__(self):
        self.pool = settings.DATABASE_POOL.keys()
        self.totals = []

        weights = settings.DATABASE_POOL.values()
        running_total = 0

        for w in weights:
            running_total += w
            self.totals.append(running_total)

    def get_random_db(self):
        """Use binary search to find the index of the database to use"""
        rnd = random.random() * self.totals[-1]
        pool_index = bisect.bisect_right(self.totals, rnd)
        return self.pool[pool_index]


class RoundRobinRouter(BasePoolRouter):
    """
    A router that cycles over a pool of databases in order, evenly distributing
    the load.
    """
    
    def __init__(self):
        super(RoundRobinRouter, self).__init__()
        
        # Shuffle the pool so the first database isn't slammed during startup.
        random.shuffle(self.pool)
        
        self.pool_cycle = itertools.cycle(self.pool)
    
    def db_for_read(self, model, **hints):
        return self.get_next_db()

    def db_for_write(self, model, **hints):
        return self.get_next_db()
    
    def get_next_db(self):
        return self.pool_cycle.next()


class MasterSlaveMixin(object):
    """
    A mixin that randomly selects from a weighted pool of slave databases
    for read operations, but uses the default database for writes.
    """

    def __init__(self):
        super(MasterSlaveMixin, self).__init__()
        self.master = settings.MASTER_DATABASE

    def db_for_write(self, model, **hints):
        """Send all writes to the master"""
        return self.master

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow any relation between two objects in the slave pool or the master.
        """
        pool = self.pool + [self.master]
        if obj1._state.db in pool and obj2._state.db in pool:
            return True
        return None

    def allow_syncdb(self, db, model):
        """Only allow syncdb on the master"""
        return db == self.master


class WeightedMasterSlaveRouter(MasterSlaveMixin, WeightedRandomRouter):
    pass


class RoundRobinMasterSlaveRouter(MasterSlaveMixin, RoundRobinRouter):
    pass


class PinningRouterMixin(object):
    """
    A mixin that pins reads to the database defined in the MASTER_DATABASE
    setting for a pre-determined period of time after a write.  Requires the
    PinningRouterMiddleware.
    """
    
    def db_for_read(self, model, **hints):
        if PinningRouterMixin.is_pinned():
            return settings.MASTER_DATABASE
        return super(PinningRouterMixin, self).db_for_read(model, **hints)
    
    def db_for_write(self, model, **hints):
        PinningRouterMixin.set_db_write()
        PinningRouterMixin.pin_thread()
        return super(PinningRouterMixin, self).db_for_write(model, **hints)
    
    
    @staticmethod
    def pin_thread():
        """
        Mark this thread as 'pinned', so that future reads will temporarily go
        to the master database for the current user.  
        """
        _locals.pinned = True
    
    @staticmethod
    def unpin_thread():
        """
        Clear the 'pinned' flag so that future reads are distributed normally.
        """
        if getattr(_locals, 'pinned', False):
            del _locals.pinned
    
    @staticmethod
    def is_pinned():
        """Check whether the current thread is pinned."""
        return getattr(_locals, 'pinned', False)
    
    @staticmethod
    def set_db_write():
        """Indicate that the database was written to."""
        _locals.db_write = True
    
    @staticmethod
    def clear_db_write():
        if getattr(_locals, 'db_write', False):
            del _locals.db_write
    
    @staticmethod
    def db_was_written():
        """Check whether a database write was performed."""
        return getattr(_locals, 'db_write', False)


class PinningWMSRouter(PinningRouterMixin, WeightedMasterSlaveRouter):
    """A weighted master/slave router that uses the pinning mixin."""
    pass


class PinningMasterSlaveRouter(PinningWMSRouter):
    """An alias to PinningWMSRouter.  This will be removed in 0.4."""
    
    def __init__(self):
        warnings.warn("This router has been renamed to 'PinningWMSRouter', "
                      "and it will be removed in the next release.",
                      DeprecationWarning)
        super(PinningMasterSlaveRouter, self).__init__()


class PinningRRMSRouter(PinningRouterMixin, RoundRobinMasterSlaveRouter):
    """A round-robin master/slave router that uses the pinning mixin."""
    pass
