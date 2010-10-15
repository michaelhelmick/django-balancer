import random
import bisect

from django.conf import settings

class WeightedRandomRouter(object):
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
    
    def db_for_read(self, model, **hints):
        return self.get_random_db()
    
    def db_for_write(self, model, **hints):
        return self.get_random_db()
    
    def allow_relation(self, obj1, obj2, **hints):
        """Allow any relation between two objects in the pool"""
        if obj1._state.db in self.pool and obj2._state.db in self.pool:
            return True
        return None

    def allow_syncdb(self, db, model):
        """Explicitly put all models on all databases"""
        return True
    
    def get_random_db(self):
        """Use binary search to find the index of the database to use"""
        rnd = random.random() * self.totals[-1]
        pool_index = bisect.bisect_right(self.totals, rnd)
        return self.pool[pool_index]


class WeightedMasterSlaveRouter(WeightedRandomRouter):
    """
    A router that randomly selected from a weighted pool of slave databases
    for read operations, but uses the default database for writes.
    """
        
    def db_for_write(self, model, **hints):
        """Send all writes to the master"""
        return settings.MASTER_DATABASE
        
    def allow_syncdb(self, db, model):
        """Only allow syncdb on the master"""
        return db == settings.MASTER_DATABASE
