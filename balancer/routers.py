import bisect
import itertools
import random

from balancer.mixins import MasterSlaveMixin, PinningMixin


class BasePoolRouter(object):
    """
    A base class for routers that use a pool of databases defined by the
    DATABASE_POOL setting.
    """

    def __init__(self):
        from django.conf import settings
        if isinstance(settings.DATABASE_POOL, dict):
            self.pool = settings.DATABASE_POOL.keys()
        else:
            self.pool = list(settings.DATABASE_POOL)

    def allow_relation(self, obj1, obj2, **hints):
        """Allow any relation between two objects in the pool"""
        if obj1._state.db in self.pool and obj2._state.db in self.pool:
            return True
        return None

    def allow_syncdb(self, db, model):
        """Explicitly put all models on all databases"""
        return True

    def allow_migrate(self, db, model):
        """Explicitly put all models on all databases"""
        return True


class RandomRouter(BasePoolRouter):
    """A router that randomly selects from a pool of databases."""

    def db_for_read(self, model, **hints):
        return self.get_random_db()

    def db_for_write(self, model, **hints):
        return self.get_random_db()

    def get_random_db(self):
        return random.choice(list(self.pool))


class WeightedRandomRouter(RandomRouter):
    """
    A router that randomly selects from a weighted pool of databases, useful
    for replication configurations where all nodes act as masters.
    """

    def __init__(self):
        from django.conf import settings
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
        return list(self.pool)[pool_index]


class RoundRobinRouter(BasePoolRouter):
    """
    A router that cycles over a pool of databases in order, evenly distributing
    the load.
    """

    def __init__(self):
        super(RoundRobinRouter, self).__init__()

        # Shuffle the pool so the first database isn't slammed during startup.
        random.shuffle(list(self.pool))

        self.pool_cycle = itertools.cycle(self.pool)

    def db_for_read(self, model, **hints):
        return self.get_next_db()

    def db_for_write(self, model, **hints):
        return self.get_next_db()

    def get_next_db(self):
        return next(self.pool_cycle)


class WeightedMasterSlaveRouter(MasterSlaveMixin, WeightedRandomRouter):
    pass


class RoundRobinMasterSlaveRouter(MasterSlaveMixin, RoundRobinRouter):
    pass


class PinningWMSRouter(PinningMixin, WeightedMasterSlaveRouter):
    """A weighted master/slave router that uses the pinning mixin."""
    pass


class PinningRRMSRouter(PinningMixin, RoundRobinMasterSlaveRouter):
    """A round-robin master/slave router that uses the pinning mixin."""
    pass
